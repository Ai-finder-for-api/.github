// CLI entry point for the line-count helper.
process.argv.splice(2, 0, 'line-count');
await import('../toolbox.mjs');

