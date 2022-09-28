using Microsoft.Azure.Functions.Extensions.DependencyInjection;
using Microsoft.Extensions.DependencyInjection;
using System;


[assembly: FunctionsStartup(typeof(LyveCloudToLogAnalytics.Startup))]
namespace LyveCloudToLogAnalytics
{
    public class Startup : FunctionsStartup
    {
        // Override configure method.
        public override void Configure(IFunctionsHostBuilder builder)
        {
            // Set up Azure Log Analytics client.
            builder.Services.AddSingleton<IAzureLogAnalyticsClient>(svc =>
            {
                var client = new AzureLogAnalyticsClient(
                  Environment.GetEnvironmentVariable("LogAnalyticsWorkspaceID"),
                  Environment.GetEnvironmentVariable("LogAnalyticsKey"));
                client.TimeStampField = "auditEntry_time_t";
                return client;
            });
        }
    }
}
