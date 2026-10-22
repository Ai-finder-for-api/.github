// CLI entry point for the log-summary helper.
process.argv.splice(2, 0, 'log-summary');
await import('../toolbox.mjs');

