"""RocksDB"""
# pylint: disable=no-member, too-few-public-methods, no-name-in-module, invalid-name
import datetime as dt
import json
import os
from enum import Enum
from typing import Any, List

import rocksdb
from pydantic import BaseModel

# from cstor.s3.core.aws import S3Object

# GB_SIZE: int = 1024 * 1024 * 1024
MB_SIZE: int = 1024 * 1024
WORK_SIZE: int = int(os.environ.get("WORK_SIZE", MB_SIZE * 200))


class MigrationStatus(Enum):
    """Migration Status"""

    PENDING = 0
    IN_PROGRESS = 1
    SUCCESS = 2
    FAILED = 3


class MigrationLog(BaseModel):
    """MigrationLog"""

    PrevState: MigrationStatus = ...
    State: MigrationStatus = ...
    Timestamp: int
    FailClass: str = ""
    FailCode: str = ""
    FailMesg: str = ""


class MigrationItem(BaseModel):
    """MigrationItem"""

    Size: int = ...
    Retries: int = ...
    State: MigrationStatus
    WorkerId: str = ""
    FailReason: str = ""
    Events: List[MigrationLog] = []


class MigrationStat(BaseModel):
    """MigrationStat"""

    ProgressSize: int = 0
    ProgressCount: int = 0
    SuccessSize: int = 0
    SuccessCount: int = 0
    FailSize: int = 0
    FailCount: int = 0


def get_utc_now() -> int:
    """Get UTC Timestamp Now"""
    dt_now: dt.datetime = dt.datetime.utcnow()
    return dt_now.timestamp()


def deserialize(data: bytes) -> MigrationItem:
    """Deserialize into MigrationItem"""
    return MigrationItem(**json.loads(data.decode("utf-8")))


def serialize(data: MigrationItem) -> bytes:
    """Serialize into bytes"""
    return data.json().encode("utf-8")


class MigrationCache(BaseModel):
    """MigrationCache"""

    user_id: str = ...
    migration_uuid: str = ...
    is_readonly: bool = True
    rdb: Any = None

    def __init__(self, **kwargs):
        """CTOR"""

        super().__init__(**kwargs)

        data_dir: str = os.environ["CSTOR_DATA_DIR"]

        opts: rocksdb.Options = rocksdb.Options()
        opts.create_if_missing = True

        db_dir: str = os.path.join(data_dir, self.user_id)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)

        db_path: str = os.path.join(db_dir, f"{self.migration_uuid}.db")

        self.rdb: rocksdb.DB = rocksdb.DB(
            db_path,
            opts,
            read_only=self.is_readonly,
        )

    # def close(self) -> None:
    #    """Closes the db"""
    #    self.rdb.close()

    def save_scan(self, data: List[any]) -> None:
        """Save scan result to rocksdb
        :param data: S3Object
        """
        batch: Any = rocksdb.WriteBatch()

        for s3_item in data:
            db_key: bytes = s3_item.Key.encode("utf-8")
            db_data: MigrationItem = MigrationItem(
                Size=s3_item.Size,
                Retries=0,
                State=MigrationStatus.PENDING,
                WorkerId="",
            )
            db_value: bytes = db_data.json().encode("utf-8")
            batch.put(db_key, db_value)

        self.rdb.write(batch)

    def get_key(self, key: str) -> MigrationItem:
        """Retrieve a single MigrationCache"""
        db_key: bytes = key.encode("utf-8")
        db_val: bytes = self.rdb.get(db_key)
        if db_val is not None:
            #
            migrate_obj: MigrationItem = MigrationItem(
                **json.loads(db_val.decode("utf-8")),
            )
            return migrate_obj

        return None

    def get_stats(self) -> MigrationStat:
        """Return current progress stats"""
        stat: MigrationStat = MigrationStat()
        db_iter = self.rdb.iterkeys()
        db_iter.seek_to_first()
        for db_key in db_iter:
            db_val: MigrationItem = deserialize(self.rdb.get(db_key))

            if db_val.State == MigrationStatus.IN_PROGRESS:
                stat.ProgressSize += db_val.Size
                stat.ProgressCount += 1
            elif db_val.State == MigrationStatus.SUCCESS:
                stat.SuccessSize += db_val.Size
                stat.SuccessCount += 1
            elif db_val.State == MigrationStatus.FAILED:
                stat.FailSize += db_val.Size
                stat.FailCount += 1

        return stat

    def update_work(self, result: dict):
        """Update the work items"""

        batch: Any = rocksdb.WriteBatch()
        for result_key in result:
            result_val: any = result[result_key]
            db_key: bytes = result_key.encode("utf-8")
            db_val: bytes = serialize(result_val)
            batch.put(db_key, db_val)

        self.rdb.write(batch)

    def get_work(self) -> dict:
        """Get the work items from source bucket scan result up to WORK_SIZE

        Conditions:
        - Fail Status
        - Pending Status
        - To add an item
        -- 1 x size summed up to WORK_SIZE

        :return: Dict of SrcKey to MigrationItem
        """
        work: dict = {}
        work_size: int = 0
        db_iter = self.rdb.iterkeys()
        db_iter.seek_to_first()

        for db_key in db_iter:
            db_val: MigrationItem = deserialize(self.rdb.get(db_key))

            if db_val.State == MigrationStatus.PENDING:
                if work_size < WORK_SIZE:
                    work_size += db_val.Size
                    db_val.State = MigrationStatus.IN_PROGRESS
                    progress_log: MigrationLog = MigrationLog(
                        PrevState=MigrationStatus.PENDING,
                        State=MigrationStatus.IN_PROGRESS,
                        Timestamp=get_utc_now(),
                    )
                    db_val.Events = db_val.Events + [progress_log]
                    work[db_key.decode("utf-8")] = db_val
                    self.rdb.put(db_key, serialize(db_val))
            elif db_val.State == MigrationStatus.FAILED and db_val.Retries < 3:
                if work_size < WORK_SIZE:
                    work_size += db_val.Size
                    db_val.State = MigrationStatus.IN_PROGRESS
                    db_val.Retries = db_val.Retries + 1
                    progress_log: MigrationLog = MigrationLog(
                        PrevState=MigrationStatus.FAILED,
                        State=MigrationStatus.IN_PROGRESS,
                        Timestamp=get_utc_now(),
                    )
                    db_val.Events = db_val.Events + [progress_log]
                    work[db_key.decode("utf-8")] = db_val
                    self.rdb.put(db_key, serialize(db_val))

        return work
