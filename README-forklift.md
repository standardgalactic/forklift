# Forklift: Python migration prototype

Additive replacement for Git Truck. Copy these files into the rewrite branch; no legacy files need to be removed. Git and Python 3.11+ are required; Matplotlib is optional. Run from the repository root.

```bash
python3 -m forklift . --output reports/self --plots
bash scripts/upstream_case_study.sh
bash scripts/verify.sh
python3 -m http.server 8000 --directory reports --bind 127.0.0.1
```

The upstream case study defaults to upstream/main excluding commits reachable from 89d8b41. Pass explicit revision, base and output as positional arguments to the script to freeze a different comparison. Reports contain HTML, full versioned JSON, CSV tables and optional SVG/PNG/PDF plots. Regenerate from JSON using `python3 -m forklift --from-json reports/self/summary.json --output reports/rebuilt`. Reports include author emails and paths; review before publication. CSV values are raw data, not spreadsheet-sanitized.

## Semantics and limitations

Snapshot files are tracked tree entries at the selected commit, not working-tree files. Submodules have unknown byte size. History includes commits reachable from revision but not base; each merge is compared to its first parent, so changes may be counted more than once across history. Renames are delete/add, binary line counts are null, and primary authors use Git mailmap. No co-author attribution, historical rename identity, caching or GitHub integration yet. Extraction launches one Git process per commit. Category patterns are ordered first-match shell globs; they describe paths, not intent or effort. Override with a TOML file containing a `[categories]` table mapping category names to arrays of patterns. The earlier exploratory case study used different merge and classification policies, so exact category counts are not promised.

## Migration gate

Run the fixture tests and compare report results against native Git before deleting original code. The fixture verifies commit count, snapshot count and bytes, categories, coupling, range exclusion and unchanged working-tree status. This is not equivalence with the original TypeScript application. Preserve the original MIT LICENSE and baseline tag. Do not replace the existing README until the migration is accepted. Ignore generated reports and Python bytecode locally.

## Version 0.2: visual reports

Every report now includes six inline and standalone SVG figures without extra dependencies: directory sizes, extension sizes, file churn, primary authors, recent monthly activity and directional architectural co-occurrence. `derived.json` preserves daily activity, monthly text churn, binary change counts and snapshot distributions. Charts show at most 20 entries (monthly activity shows the last 20 observed months); full data remain in JSON. Snapshot sizes are logical tracked blob bytes, not disk usage. Churn is not net growth; binary changes are counted separately. The heatmap includes zero co-occurrences and uses row-normalized percentages. Existing schema-1 JSON reports can be re-rendered without Git. No legacy files are removed.

## Revision 0.3

The dashboard includes a daily calendar, commit-size histogram and expandable directory explorer. Binary changes contribute zero textual lines to the histogram. Use `python3 -m forklift . --output reports/self --snapshots 60` to generate exact sampled first-parent tree sizes and file counts, with CSV and SVG exports. Sampling is by commit order, not elapsed time; blob sizes are logical snapshot sizes, not Git object storage. Archived JSON retains snapshots for offline rendering. No original application files are removed.

## v0.4: collections and artifacts

    python3 -m forklift scan ~/projects --depth 2 --output reports/collection --individual
    python3 -m forklift compare ~/laboratory ~/research --output reports/comparison
    python3 scripts/benchmark.py . --output reports/benchmark

Scan depth counts directory edges; scanning stops at repository roots (including bare repositories and linked worktrees), skips hidden directories and does not follow symlink directories. Comparison analyzes HEAD of each repository. `--individual` generates full per-repository reports; `--github` optionally calls authenticated `gh repo view` and stores metadata or errors in collection.json. No network by default. Failed repositories are recorded and the CLI exits nonzero. Collection charts show up to 20 repositories; CSV and JSON retain all successful rows. Author emails in individual reports should be reviewed before publication.

Single-repository reports now include artifact classifications and a proportional slice-and-dice treemap with path tooltips. Classification is heuristic; PDFs are documents/media, not presumed generated. Zero-byte files and submodules are omitted from the area chart. Existing schema-1 JSON remains supported. Rename identity is still deferred. Benchmark RSS is the Python process peak on Linux, not total subprocess memory; Git call counts measure wrapper invocations. Use fresh output directories to avoid stale files. See MIGRATION.md for status.

## Version 0.5

`--renames` opts into Git's 50% similarity rename detection. Rename records contain `old_path` and destination `path`; both categories count toward footprints, but modification counts use the destination. This is edge-level tracking, not global file identity. Default behavior remains deletion/addition for comparison with earlier reports.

`--cache reports/cache.sqlite` stores complete analyses keyed by repository path, resolved revision and base, ordered rules, rename mode, version, Git configuration and working-tree mailmap. Cache hits preserve original generation time. Delete the cache after changes to external attributes, Git version, or other environmental inputs; cache is opt-in and may contain author emails. Keep it outside published reports if privacy matters.

`compare` and `scan` accept `--jobs N` for parallel repository analysis (default 1). Example:

```bash
python3 -m forklift compare ~/laboratory ~/research ~/cosmology ~/forklift --output reports/comparison --cache ~/.cache/forklift/analysis.sqlite --jobs 4 --renames
```

Both dashboard styles explicitly use a light background. Batched extraction, incremental caching and global rename lineage remain deferred.

## v0.6: Interactive exploration

Individual reports now include a proportional directory drill-down, searchable commit selector with changed paths, file co-occurrence network, and searchable observed rename transitions. `relationships.json` preserves the network and rename records. The network is restricted to the 100 most frequently changed destination paths and the 200 highest-count edges; duplicate paths within a commit count once. The circular layout is not a dependency graph. Rename transitions are observations, not globally unique file identities. Zero-byte entries remain available in the existing directory explorer. All controls operate offline.

Regenerate an existing report without Git extraction:

```bash
python3 -m forklift --from-json reports/self/summary.json --output reports/self-v06
```

Generate a collection with interactive individual reports using `compare ... --individual --renames`. Animation, incremental caching and batched extraction remain deferred. The version change invalidates v0.5 cache keys; archived JSON remains compatible.

### v0.6.1 readability

Charts use opaque white backgrounds, black labels, larger fonts and full-width panels. Narrow windows can scroll horizontally instead of shrinking charts below 900 CSS pixels. Regenerate reports to apply the changes.

### v0.6.2: native HTML dashboards

Both report types now use native text, sortable tables and CSS bars with system light/dark colors. SVG files remain available under Optional SVG exports, but are not embedded. Directory drill-down includes zero-byte entries; the coupling explorer uses a file selector and a sortable retained-pair table rather than a network diagram. Daily activity and sampled historical snapshots are available as tables. Existing JSON reports can be regenerated with `--from-json`. Browser rendering has not been manually verified.
