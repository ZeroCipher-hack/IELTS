# Student interface design system

The production interface uses `frontend/app/globals.css`. Its single `:root` block owns light theme colors and spacing; `html[data-theme="dark"]` overrides theme tokens. Component rules use tokens rather than embedded colors. Teal is the decorative accent, with red reserved for errors. H1/H2/H3 weights are 650/600/500. Spacing follows 4, 8, 12, 16, 24, 32 and 48 pixels.

Static panels have no elevation. Clickable target and skill cards have a small lift/shadow. Reduced-motion preferences disable animation and smooth question navigation. Theme preference persists locally, with system preference used until the user chooses a theme.

The historical `/design` preview imports its own `legacy.css`. Its scope is limited to documents containing `data-design-preview`, including portalled demo dialogs. Do not import this stylesheet from the root layout or add production overrides to it.

Catalog and history loading states are independent. Skeletons display while those requests load; background assessment refreshes keep current data visible. Exam progress counts nonblank answers against actual question IDs, independently of review flags and server-save status. Writing entries count as answered tasks, not completed/graded essays.

Unavailable exam buttons open availability information using a secondary style. No purchase is simulated. Speaking has no confirmed release date; do not add a date without an agreed schedule. Payments and unpublished test materials remain unavailable.

Validation: production build and TypeScript passed; theme initialization checked with stored/system preferences and blocked storage. Production HTML references only the main stylesheet, while `/design` additionally references the isolated legacy stylesheet. Full browser visual verification is still pending (no browser executable in the environment). Check desktop/mobile, both themes, keyboard focus, and print output when a browser is available.
