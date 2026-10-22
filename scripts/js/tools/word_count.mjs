// CLI entry point for the word-count helper.
process.argv.splice(2, 0, 'word-count');
await import('../toolbox.mjs');

