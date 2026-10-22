// CLI entry point for the merge-json helper.
process.argv.splice(2, 0, 'merge-json');
await import('../toolbox.mjs');

