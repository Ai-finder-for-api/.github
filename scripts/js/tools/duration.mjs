// CLI entry point for the duration helper.
process.argv.splice(2, 0, 'duration');
await import('../toolbox.mjs');

