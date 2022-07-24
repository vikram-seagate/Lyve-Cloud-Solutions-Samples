const express = require("express");
const cors = require("cors");
const app = express();
const port = 10086;

const ALIBABARoutes = require("./Routes/alibaba.routes");
const AzureRoutes = require("./Routes/azure.routes");
const LyveRoutes = require("./Routes/lyve.routes");
const GoogleRoutes = require('./Routes/google.routes')
const GeneralS3Routes = require("./Routes/generals3.routes");
const CommonRoutes = require("./Routes/common.routes");
const MigrationTasksRoutes = require("./Routes/migration-tasks.routes");
const SynchronizationTasksRoutes = require("./Routes/synchronization-tasks.routes");
const SynchronizationJobsRoutes = require("./Routes/synchronization-jobs.routes");

const MongoDAO = require("./Database/MongoDAO");
const mongoDAO = new MongoDAO();

const SyncTaskManager = require("./Database/SyncTaskManager");
const syncTaskManager = new SyncTaskManager(mongoDAO);
mongoDAO.setupCallbacks.push(() => {
    syncTaskManager.setupExistingTasks().then();
});

mongoDAO.connect().then(() => {

    app.use(express.json());
    app.use(cors());

    app.use("*", (req, res, next) => {
        req.mongoDAO = mongoDAO;
        req.syncTaskManager = syncTaskManager;
        next();
    });

    app.use("/lyve", LyveRoutes);
    app.use("/general-s3", GeneralS3Routes);
    app.use("/alibaba-cloud", ALIBABARoutes);
    app.use("/azure", AzureRoutes);
    app.use("/common", CommonRoutes);
    app.use("/migration-tasks", MigrationTasksRoutes);
    app.use("/synchronization-jobs", SynchronizationJobsRoutes);
    app.use("/synchronization-tasks", SynchronizationTasksRoutes);
    app.use("/google", GoogleRoutes);

    app.listen(port, () => {
        console.log(`server is running at port ${port}`);
    });
});
