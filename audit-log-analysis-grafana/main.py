# Copyright (c) 2021 Seagate Technology LLC and/or its Affiliates

from apscheduler.schedulers.blocking import BlockingScheduler
from job import executor
from datetime import datetime, timezone, timedelta
from datasources import influxdb
import os

def Streaming():

    

    if influxdb.is_init_influx():
        # initail innflux by upload data last 30 day to influxdb
        OnetimePulling(720)
    else:
        if os.path.exists('lastr_run.time'):
            with open('lastr_run.time','rt') as fp:
                dt_str   = fp.read()
                cur_dt   = datetime.now(timezone.utc)
                last_dt  = datetime.strptime(dt_str,'%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
                delta_dt = cur_dt - last_dt
                delta_dt_hour = int(delta_dt.total_seconds()/3600)
                if delta_dt_hour >= 1:
                    OnetimePulling(delta_dt_hour)
                else:
                    print(delta_dt_hour)
                    

    print("LogGateWay is running on Streaming mode")
    scheduler = BlockingScheduler()
    scheduler.add_job(executor.run,trigger='cron',minute='1',hour='*') 
    print('Press Ctrl+C to exit')

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass

def OnetimePulling(hours_delta = 7):
    print("LogGateWay is running on OnetimePulling mode")
    from_date = datetime.now(timezone.utc) - timedelta(hours=hours_delta)
    executor.run(from_date)

if __name__ == '__main__':


    Streaming()
    # OnetimePulling()
