import axios from "axios";

// export const serverURL = "http://localhost:10086";
export const serverURL = `http://${window.location.hostname}:10086`;

export const apiCreateMigrationTasks = (data) => {
    data.forEach(task => {
        task.status = "NOT_STARTED";
        task.bytes_migrated = 0;
    });
    console.log(data);
    return axios.post(`${serverURL}/migration-tasks`, data);
};

export const apiFetchMigrationTasks = (source_platform) => {
    return axios.get(`${serverURL}/migration-tasks?source_platform=${source_platform}`);
};


export const apiUpdateMigrationTaskProgress = (id, data) => {
    return axios.put(`${serverURL}/migration-tasks/${id}`, data);
};

export const apiRerunMigrationTask = (id) => {
    return axios.post(`${serverURL}/migration-tasks/${id}/rerun`);
};

export const apiEnableSyncTask = (id) => {
    return axios.post(`${serverURL}/synchronization-tasks/${id}/enable`);
};

export const apiPauseSyncTask = (id) => {
    return axios.post(`${serverURL}/synchronization-tasks/${id}/pause`);
};

export const apiDeleteMigrationTask = (id) => {
    return axios.delete(`${serverURL}/migration-tasks/${id}`);
};

export const apiDeleteSyncTask = (id) => {
    return axios.delete(`${serverURL}/synchronization-tasks/${id}`);
};

export const apiCreateSynchronizationTask = (data) => {
    return axios.post(`${serverURL}/synchronization-tasks`, data);
};

export const apiFetchSynchronizationTasks = (source_platform) => {
    return axios.get(`${serverURL}/synchronization-tasks?source_platform=${source_platform}`);
};

export const apiFetchSynchronizationJobs = (source_platform) => {
    return axios.get(`${serverURL}/synchronization-jobs?source_platform=${source_platform}`);
};
