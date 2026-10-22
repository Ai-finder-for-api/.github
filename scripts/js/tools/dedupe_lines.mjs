// CLI entry point for the dedupe-lines helper.
process.argv.splice(2, 0, 'dedupe-lines');
await import('../toolbox.mjs');

