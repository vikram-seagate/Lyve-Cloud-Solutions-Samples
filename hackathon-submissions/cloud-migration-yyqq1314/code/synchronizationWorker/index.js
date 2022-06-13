const SynchronizationWorker = require("./SynchronizationWorker");

const worker = new SynchronizationWorker();

// Begin reading from stdin so the process does not exit.
process.stdin.resume();

// Using a single function to handle multiple signals
function handle(signal) {
    console.log(`Received ${signal}`);
    worker.shutdown();
}

process.on("SIGINT", handle);
process.on("SIGTERM", handle);

worker.start().then();




