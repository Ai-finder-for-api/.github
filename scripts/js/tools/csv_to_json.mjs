// CLI entry point for the csv-to-json helper.
process.argv.splice(2, 0, 'csv-to-json');
await import('../toolbox.mjs');

