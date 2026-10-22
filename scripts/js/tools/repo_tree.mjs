// CLI entry point for the repo-tree helper.
process.argv.splice(2, 0, 'repo-tree');
await import('../toolbox.mjs');

