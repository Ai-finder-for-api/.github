// CLI entry point for the json-format helper.
process.argv.splice(2, 0, 'json-format');
await import('../toolbox.mjs');

