// CLI entry point for the json-sort helper.
process.argv.splice(2, 0, 'json-sort');
await import('../toolbox.mjs');

