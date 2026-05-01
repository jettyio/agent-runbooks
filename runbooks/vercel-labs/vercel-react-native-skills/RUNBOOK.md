---
version: "1.0.0"
evaluation: programmatic
agent: claude-code
model: claude-sonnet-4-6
snapshot: python312-uv
origin:
  url: "https://skills.sh/vercel-labs/agent-skills/vercel-react-native-skills"
  source_host: "skills.sh"
  source_title: "React Native Skills"
  imported_at: "2026-05-01T00:00:00Z"
  imported_by: "skill-to-runbook-converter@1.0.0"
  attribution:
    collection_or_org: "vercel-labs"
    skill_name: "vercel-react-native-skills"
    confidence: "high"
---

# React Native Skills — Agent Runbook

## Objective

Apply React Native and Expo best practices for building performant mobile applications. This runbook guides the agent through auditing and improving React Native codebases by applying prioritized rules across list performance, animations, navigation, UI patterns, state management, rendering, monorepo configuration, and platform-specific optimizations. Use this runbook when building React Native components, optimizing list performance, implementing animations with Reanimated, or working with native modules. It is triggered by tasks involving React Native, Expo, mobile performance, or native platform APIs.

---

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to `/app/results`.
The task is NOT complete until every file exists and is non-empty. No exceptions.**

| File | Description |
|------|-------------|
| `/app/results/summary.md` | Executive summary of changes applied, rules triggered, and issues found |
| `/app/results/validation_report.json` | Structured validation results with stages, results, and `overall_passed` |
| `/app/results/applied_rules.json` | List of rules applied with category, rule name, file(s) changed, and rationale |
| `/app/results/diff.patch` | Unified diff of all code changes made (empty if no changes required) |

---

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Results directory | `/app/results` | Output directory for all results |
| Target directory | *(required)* | Path to the React Native / Expo project to audit and improve |
| Rule categories | `all` | Comma-separated list of rule category prefixes to apply (`list-performance`, `animation`, `navigation`, `ui`, `react-state`, `rendering`, `monorepo`, `fonts`, `imports`). Use `all` to apply every category. |
| Dry run | `false` | If `true`, report findings and proposed changes but do NOT modify files |

---

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `node` / `npm` | CLI | Yes | Required to run React Native project tooling |
| `expo-cli` or `react-native-cli` | CLI | Conditional | Needed for project scaffolding and build verification |
| `FlashList` (`@shopify/flash-list`) | npm package | Recommended | High-performance replacement for FlatList |
| `expo-image` | npm package | Recommended | Optimized image component for Expo projects |
| `react-native-reanimated` | npm package | Recommended | GPU-accelerated animations |
| `react-native-gesture-handler` | npm package | Recommended | Native gesture system |
| `nativewind` | npm package | Optional | Tailwind CSS utility styling for React Native |

---

## Step 1: Environment Setup

Verify the environment and locate the React Native project to audit.

```bash
echo "=== Environment Setup ==="

# Verify node is available
node --version || { echo "ERROR: node not found"; exit 1; }
npm --version || { echo "ERROR: npm not found"; exit 1; }

# Create output directory
mkdir -p /app/results

# Verify target directory exists and contains a React Native project
TARGET_DIR="${TARGET_DIR:-$(pwd)}"
if [ ! -f "$TARGET_DIR/package.json" ]; then
  echo "ERROR: No package.json found at $TARGET_DIR"
  exit 1
fi

# Check for React Native dependency
if grep -q "react-native" "$TARGET_DIR/package.json"; then
  echo "PASS: React Native project detected at $TARGET_DIR"
else
  echo "WARNING: react-native not found in package.json — verify this is an RN project"
fi

echo "Setup complete."
```

---

## Step 2: Audit List Performance (CRITICAL)

Apply list performance rules — these have the highest impact on perceived app speed.

```bash
echo "=== Step 2: List Performance Audit ==="
```

Check for the following patterns and apply fixes:

| Rule | Check | Fix |
|------|-------|-----|
| `list-performance-virtualize` | Any `FlatList` with large datasets | Replace with `FlashList` from `@shopify/flash-list` |
| `list-performance-item-memo` | List item components without `React.memo` | Wrap item components in `React.memo` |
| `list-performance-callbacks` | Unstable callback refs passed to list items | Wrap callbacks in `useCallback` |
| `list-performance-inline-objects` | Inline `style={{ ... }}` objects inside list renders | Extract to `StyleSheet.create` |
| `list-performance-function-references` | Functions defined inside render that are passed as props | Hoist functions outside the component or memoize |
| `list-performance-images` | `Image` components in list items without explicit dimensions | Add explicit `width` and `height`; use `expo-image` |
| `list-performance-item-expensive` | Expensive computation inside list item render | Move to `useMemo` or lift above the list |
| `list-performance-item-types` | Heterogeneous lists without `getItemType` | Add `getItemType` prop to `FlashList` |

---

## Step 3: Audit Animation Patterns (HIGH)

Apply animation rules to ensure GPU-accelerated, jank-free animations.

```bash
echo "=== Step 3: Animation Audit ==="
```

| Rule | Check | Fix |
|------|-------|-----|
| `animation-gpu-properties` | Animations driving layout properties (`width`, `height`, `top`, `left`) | Refactor to animate only `transform` and `opacity` |
| `animation-derived-value` | Computed animation values using JS-thread interpolation | Replace with `useDerivedValue` from `react-native-reanimated` |
| `animation-gesture-detector-press` | `Pressable` inside `GestureDetector` for tap handling | Replace with `Gesture.Tap()` to avoid gesture collision |

---

## Step 4: Audit Navigation (HIGH)

Verify native navigator usage for best performance.

```bash
echo "=== Step 4: Navigation Audit ==="
```

| Rule | Check | Fix |
|------|-------|-----|
| `navigation-native-navigators` | JS-based navigators (`createStackNavigator` without `@react-navigation/native-stack`) | Replace with `createNativeStackNavigator` and `createNativeBottomTabNavigator` |

---

## Step 5: Audit UI Patterns (HIGH)

Apply UI component best practices.

```bash
echo "=== Step 5: UI Patterns Audit ==="
```

| Rule | Check | Fix |
|------|-------|-----|
| `ui-expo-image` | Use of `<Image>` from `react-native` | Replace with `<Image>` from `expo-image` for caching and performance |
| `ui-image-gallery` | Custom image lightbox implementations | Replace with `Galeria` component |
| `ui-pressable` | `TouchableOpacity` usage | Replace with `Pressable` for finer hit-slop and feedback control |
| `ui-safe-area-scroll` | `ScrollView` without safe area insets | Wrap with `useSafeAreaInsets` or use `SafeAreaScrollView` |
| `ui-scrollview-content-inset` | Overlap between fixed headers and content | Use `contentInset` and `contentOffset` on `ScrollView` |
| `ui-menus` | Custom long-press action menus | Replace with `@zeego/menu` or platform native context menus |
| `ui-native-modals` | JS-animated modal sheets | Use `expo-router` sheet or `@gorhom/bottom-sheet` with native driver |
| `ui-measure-views` | `ref.measure()` calls for layout info | Replace with `onLayout` callback |
| `ui-styling` | Mixed inline styles and scattered `StyleSheet` calls | Standardize on `StyleSheet.create` or Nativewind utility classes |

---

## Step 6: Audit State Management (MEDIUM)

Apply state management rules to reduce unnecessary re-renders.

```bash
echo "=== Step 6: State Management Audit ==="
```

| Rule | Check | Fix |
|------|-------|-----|
| `react-state-minimize` | Components subscribing to large Zustand/Redux slices | Use selector functions to subscribe to minimal state slices |
| `react-state-dispatcher` | Callback props drilled through many levels | Extract a dispatcher context or use `useReducer` dispatch |
| `react-state-fallback` | Missing loading/fallback states on first render | Add skeleton or placeholder UI before data arrives |
| `react-compiler-destructure-functions` | Functions passed as props not compatible with React Compiler | Destructure props before passing to enable compiler optimization |
| `react-compiler-reanimated-shared-values` | Shared values accessed inline without `useAnimatedProps` | Wrap shared value reads in `useAnimatedProps` or `useAnimatedStyle` |

---

## Step 7: Audit Rendering (MEDIUM)

Fix rendering anti-patterns that cause runtime warnings or visual glitches.

```bash
echo "=== Step 7: Rendering Audit ==="
```

| Rule | Check | Fix |
|------|-------|-----|
| `rendering-text-in-text-component` | Raw string literals rendered outside `<Text>` | Wrap all text in `<Text>` components |
| `rendering-no-falsy-and` | `{count && <Component />}` patterns | Replace with ternary: `{count ? <Component /> : null}` |

---

## Step 8: Audit Monorepo Configuration (MEDIUM)

For monorepo setups, apply dependency isolation rules.

```bash
echo "=== Step 8: Monorepo Audit ==="
```

| Rule | Check | Fix |
|------|-------|-----|
| `monorepo-native-deps-in-app` | Native dependencies declared in shared packages | Move native deps to the app's `package.json` |
| `monorepo-single-dependency-versions` | Duplicate versions of the same package across workspace packages | Hoist to root `package.json` or enforce single version with `resolutions` |

---

## Step 9: Audit Configuration (LOW)

Apply low-impact but good-practice configuration rules.

```bash
echo "=== Step 9: Configuration Audit ==="
```

| Rule | Check | Fix |
|------|-------|-----|
| `fonts-config-plugin` | Custom fonts loaded via `useFonts` without a config plugin | Add `expo-font` config plugin to `app.config.js` |
| `imports-design-system-folder` | Design system components imported from scattered paths | Consolidate into a `/design-system` barrel export |
| `js-hoist-intl` | `new Intl.NumberFormat(...)` created inside render functions | Hoist to module scope or `useMemo` |

---

## Step 10: Iterate on Errors (max 3 rounds)

If any automated fix caused a build failure or test failure:

1. Read the error from the relevant log
2. Identify which rule change introduced the regression
3. Revert that specific change or apply an alternative fix
4. Re-run the relevant check
5. Repeat up to 3 rounds

### Common Fixes

| Issue | Fix |
|-------|-----|
| FlashList missing `estimatedItemSize` | Add `estimatedItemSize={72}` (or measure average item height) |
| `useCallback` dependency warnings after memoization | Ensure dependency array is accurate; use `eslint-plugin-react-hooks` |
| Reanimated `useAnimatedStyle` not running on UI thread | Add `'worklet'` directive inside the callback |
| Gesture handler setup error | Call `GestureHandlerRootView` at the app root |
| expo-image peer dependency conflict | Run `npx expo install expo-image` to resolve correct version |

---

## Step 11: Write Results

Serialize all findings and applied changes to the output files.

```bash
echo "=== Step 11: Writing Results ==="

# applied_rules.json is written during Steps 2-9 as rules are applied
# diff.patch is created from git diff if the project is a git repo

if git -C "${TARGET_DIR}" rev-parse --is-inside-work-tree 2>/dev/null; then
  git -C "${TARGET_DIR}" diff > /app/results/diff.patch
  echo "PASS: diff.patch written"
else
  echo "" > /app/results/diff.patch
  echo "INFO: Not a git repo — diff.patch written as empty"
fi

echo "Results written."
```

---

## Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json" \
  "$RESULTS_DIR/applied_rules.json" \
  "$RESULTS_DIR/diff.patch"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
echo "=== END VERIFICATION ==="
```

### Checklist

- [ ] `summary.md` exists with count of rules applied per category
- [ ] `validation_report.json` exists with `overall_passed` field
- [ ] `applied_rules.json` lists every rule that was triggered
- [ ] `diff.patch` exists (may be empty if no changes needed)
- [ ] No unresolved `TODO` or `FIXME` markers left in modified files
- [ ] Build/test commands still pass after changes

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

---

## Tips

- **Apply rules by priority order.** Fix list performance first (CRITICAL), then animations and navigation (HIGH), then lower-priority categories. This ensures the highest-impact changes are never blocked by lower-priority refactors.
- **Use `npx expo install` for package version resolution.** When adding `expo-image`, `react-native-reanimated`, or other Expo SDK packages, always use `npx expo install <package>` so the version is pinned to match your SDK version.
- **FlashList requires `estimatedItemSize`.** Always measure a representative item to provide an accurate estimate; the default causes warnings and suboptimal recycling.
- **Reanimated worklets must be pure.** Functions passed to `useAnimatedStyle` or `useAnimatedProps` cannot reference JS-thread closures — capture any needed values via shared values.
- **`attribution_confidence: high`** — This skill was confirmed from the GitHub SKILL.md at `vercel-labs/agent-skills`. Rule files can be read individually from `rules/` in that repository for detailed examples.
