// CLI entry point for the text-stats helper.
process.argv.splice(2, 0, 'text-stats');
await import('../toolbox.mjs');

