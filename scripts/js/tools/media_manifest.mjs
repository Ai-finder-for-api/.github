// CLI entry point for the media-manifest helper.
process.argv.splice(2, 0, 'media-manifest');
await import('../toolbox.mjs');

