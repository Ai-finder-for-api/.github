// CLI entry point for the timestamp helper.
process.argv.splice(2, 0, 'timestamp');
await import('../toolbox.mjs');

