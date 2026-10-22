// CLI entry point for the csv-summary helper.
process.argv.splice(2, 0, 'csv-summary');
await import('../toolbox.mjs');

