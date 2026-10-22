// CLI entry point for the sort-lines helper.
process.argv.splice(2, 0, 'sort-lines');
await import('../toolbox.mjs');

