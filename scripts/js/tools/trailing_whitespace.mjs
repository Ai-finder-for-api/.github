// CLI entry point for the trailing-whitespace helper.
process.argv.splice(2, 0, 'trailing-whitespace');
await import('../toolbox.mjs');

