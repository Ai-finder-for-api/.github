// CLI entry point for the normalize-newlines helper.
process.argv.splice(2, 0, 'normalize-newlines');
await import('../toolbox.mjs');

