// CLI entry point for the relative-path helper.
process.argv.splice(2, 0, 'relative-path');
await import('../toolbox.mjs');

