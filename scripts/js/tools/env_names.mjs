// CLI entry point for the env-names helper.
process.argv.splice(2, 0, 'env-names');
await import('../toolbox.mjs');

