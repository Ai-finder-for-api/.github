// CLI entry point for the diff-json helper.
process.argv.splice(2, 0, 'diff-json');
await import('../toolbox.mjs');

