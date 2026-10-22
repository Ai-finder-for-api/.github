// CLI entry point for the json-minify helper.
process.argv.splice(2, 0, 'json-minify');
await import('../toolbox.mjs');

