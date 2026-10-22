// CLI entry point for the json-to-csv helper.
process.argv.splice(2, 0, 'json-to-csv');
await import('../toolbox.mjs');

