// CLI entry point for the validate-json helper.
process.argv.splice(2, 0, 'validate-json');
await import('../toolbox.mjs');

