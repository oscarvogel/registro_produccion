---
name: Emerald Operations
source: frontend/src/style.css
themes:
  light:
    background: '#f5f6f3'
    background-soft: '#edf0ea'
    surface: '#ffffff'
    surface-muted: '#f0f2ed'
    border: '#dfe5dc'
    border-strong: '#c2c9bf'
    foreground: '#151813'
    foreground-muted: '#687064'
    foreground-soft: '#969f92'
    primary: '#10b981'
    on-primary: '#002113'
    secondary: '#4edea3'
    on-secondary: '#003829'
    warning: '#ef9f27'
    on-warning: '#412402'
    error: '#ff4d5e'
    on-error: '#40000e'
    tertiary: '#ff7886'
    on-tertiary: '#67011c'
  dark:
    background: '#090e0b'
    background-soft: '#0f1511'
    surface: '#141c17'
    surface-muted: '#101712'
    border: '#222d26'
    border-strong: '#34423a'
    foreground: '#f2f8f4'
    foreground-muted: '#b8c7bd'
    foreground-soft: '#829286'
    primary: '#10b981'
    on-primary: '#002113'
    secondary: '#95d3ba'
    on-secondary: '#003829'
    warning: '#ef9f27'
    on-warning: '#412402'
    error: '#ff7886'
    on-error: '#40000e'
    tertiary: '#ff7886'
    on-tertiary: '#67011c'
  persistent-navigation:
    background: '#07100c'
    header: '#090e0b'
    surface: '#141c17'
    border: '#222d26'
    active-background: '#0f2a1e'
    accent: '#10b981'
    accent-strong: '#6ffbbe'
    status-text: '#9fe1cb'
  status:
    success: '#10b981'
    info-light: '#e1f5ee'
    info: '#1d9e75'
    warning-light: '#faeeda'
    error-light: '#ffdad6'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 36px
    fontWeight: '800'
    lineHeight: 44px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
  label-sm:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 14px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  unit: 4px
  gutter: 16px
  container-padding: 24px
  sidebar-width: 256px
  stack-sm: 8px
  stack-md: 16px
  stack-lg: 24px
---

## Brand & Style
The brand identity is rooted in industrial precision and operational efficiency. It targets technical administrators and logistics managers who require high-density data visualization and clear status indicators.

The design style is **Corporate Modern** with a strong emphasis on **Tonal Layering**. It uses a forest/emerald palette with neutral surfaces and high-contrast semantic states. The aesthetic is utilitarian yet refined, employing subtle borders and clear typography to create a sense of organized complexity. The UI should feel reliable, high-tech, and structurally sound.

## Color System
`frontend/src/style.css` is the technical source of truth for the implemented palette. The system uses semantic roles instead of treating raw colors as interchangeable decoration.

### Dark theme

- **Background**: `#090e0b` (`--app-bg`) is the deepest application canvas.
- **Background soft**: `#0f1511` (`--app-bg-soft`) separates secondary areas from the canvas.
- **Surface**: `#141c17` (`--app-surface`) is used by cards, panels and primary containers.
- **Muted surface**: `#101712` (`--app-surface-muted`) supports inputs, filters and lower-emphasis areas.
- **Borders**: `#222d26` and `#34423a` define normal and strong boundaries.
- **Foregrounds**: `#f2f8f4` is the primary text, `#b8c7bd` is muted text and `#829286` is soft text.
- **Tonal scale**: the dark surface containers progress through `#090e0b`, `#0f1511`, `#141c17`, `#1a241e` and `#223028`.

### Light theme

- **Background**: `#f5f6f3` (`--app-bg`) provides the neutral canvas.
- **Background soft**: `#edf0ea` (`--app-bg-soft`) separates supporting areas.
- **Surface**: `#ffffff` (`--app-surface`) is used by cards, forms, tables and raised content.
- **Muted surface**: `#f0f2ed` (`--app-surface-muted`) supports inputs, filters and secondary areas.
- **Borders**: `#dfe5dc` and `#c2c9bf` define normal and strong boundaries.
- **Foregrounds**: `#151813` is the primary text, `#687064` is muted text and `#969f92` is soft text.

### Semantic responsibilities

- **Primary emerald**: `#10b981` is the functional pulse for primary actions, active states, online status and key accents. Its semantic foreground is `#002113` (`--color-on-primary`).
- **Secondary teal**: `#4edea3` in Light and `#95d3ba` in Dark supports operational secondary actions and information states. Use the `on-secondary` foreground token for solid surfaces.
- **Warning amber**: `#ef9f27` signals attention, pending work and operational caution. Solid amber uses the dark `#412402` foreground (`--color-on-warning`); light/dark container variants use their corresponding warning tokens.
- **Error/coral**: `#ff4d5e` in Light and `#ff7886` in Dark identify failures and critical operational feedback. Use `on-error` or the appropriate dark-mode foreground token rather than defaulting to white.
- **Tertiary coral/rose**: `#ff7886` is the tertiary accent. Tertiary is coral/rose, not amber; `#67011c` is its semantic foreground.
- **Success**: reuses the emerald family for confirmed or synchronized states.
- **Info**: uses teal/emerald tones (`#1d9e75` in Light and `#95d3ba` in Dark) for neutral operational information.
- **State indicators**: online and active states may use a restrained emerald glow; the glow reinforces status and does not replace text or labels.

Solid semantic backgrounds must use their `on-*` foreground token. White text is not the default for primary, secondary, warning, error or tertiary surfaces.

## Navigation Theme Strategy (Light/Dark)

La sidebar de escritorio y el header móvil son superficies de navegación de marca. Permanecen oscuros tanto en `Light` como en `Dark`; esta persistencia es intencional y no una superficie pendiente de adaptación al tema.

El modo `Light` aplica principalmente al canvas principal, cards, tablas, formularios, superficies, modales y demás contenido. La navegación conserva su fondo oscuro para reforzar la identidad visual, mantener una orientación espacial estable y sostener el contraste con el contenido claro.

### Navigation state contract

- **Estado activo**: borde/acento esmeralda, superficie verde profunda y texto blanco.
- **Hover y focus**: superficie forestal sutil, texto blanco y anillo de foco visible.
- **Usuario y servidor**: nombre, rol y estado de conexión usan texto claro sobre la superficie oscura; el indicador esmeralda identifica conexión disponible.
- **Badges**: cuando se renderizan, mantienen el color funcional de advertencia con el foreground semántico `on-warning` y permanecen visibles en navegación expandida o como indicador compacto en navegación colapsada.
- **Cambio de tema**: actualiza el contenido principal, pero no convierte la sidebar ni el header móvil en superficies claras.
- **Navegación colapsada**: conserva iconos, estado activo, indicadores y foco; las etiquetas siguen disponibles mediante `title` o nombre accesible.

No se deben reemplazar estas superficies por fondos claros como parte de una futura adaptación del modo `Light`, salvo que se revise explícitamente esta decisión de identidad visual.

## Typography
The system relies exclusively on **Inter**, declared in `frontend/src/style.css`, to maintain a neutral, systematic, and highly legible appearance across data-dense tables and technical labels.

- **Display**: 36px / 44px, weight 800, for the main page statement.
- **Headlines**: 24px / 32px, weight 700, and 18px / 24px, weight 600, for page and section hierarchy.
- **Body**: 16px / 24px and 14px / 20px for descriptions, tables and supporting content.
- **Labels**: 12px / 16px, weight 600, and 11px / 14px, weight 500, for compact metadata and section labels.
- **Hierarchy**: Emphasized through weight shifts and restrained size changes rather than decoration.
- **Density**: Line heights stay between 1.2 and 1.5 to maximize vertical information density.

## Layout & Spacing
The layout follows a **Fixed-Sidebar Fluid-Canvas** model. 

- **Sidebar**: Fixed at 256px (`md:w-64`) on desktop, utilizing a vertical stack for navigation.
- **Grid**: A standard 12-column system is used within the main canvas, but components primarily organize into 1, 2, or 4 column spans depending on screen width.
- **Breakpoints**: 
    - **Mobile (<768px)**: Sidebar hidden (hamburger menu required), 16px margins, single-column cards.
    - **Tablet (768px - 1280px)**: Sidebar visible, 2-column metric grid.
    - **Desktop (>1280px)**: 4-column metrics, 2:1 ratio for main content vs. sidebar utility panels.
- **Rhythm**: Spacing is strictly based on a 4px baseline unit.

## Elevation & Depth
Depth is achieved through **Tonal Layering** and **Subtle Outlines** rather than heavy shadows. The hierarchy adapts to the content theme while preserving the same semantic roles.

- **Dark hierarchy**: the `#090e0b` canvas progresses through `#0f1511`, `#141c17`, `#1a241e` and `#223028` for increasingly raised content.
- **Light hierarchy**: the `#f5f6f3` canvas uses `#edf0ea`, `#f0f2ed` and `#ffffff` for supporting, muted and raised surfaces.
- **Boundaries**: cards and containers use the theme border tokens (`#222d26` / `#34423a` in Dark and `#dfe5dc` / `#c2c9bf` in Light).
- **Interaction Depth**: Hover states on interactive cards should transition the border color to `primary/50` or `outline-variant` and introduce a subtle glow (`shadow-sm`) rather than an offset shadow.
- **Overlays**: Modals and mobile menus use a backdrop blur (8px-12px) to maintain context while isolating the interaction.

## Shapes
The shape language is "Soft-Technical." Most containers use a 0.25rem (4px) or 0.5rem (8px) radius to maintain a precise, structured feel.

- **Cards/Containers**: 12px (rounded-xl) for main dashboard sections.
- **Buttons/Inputs**: 8px (rounded-lg) for standard actions.
- **Navigation/Status Chips**: Full-pill (rounded-full) to provide a distinct visual contrast against the rigid rectangular grid.
- **Small Accents**: 4px for mini-avatars or category icons.

## Components
- **Buttons**:
    - *Primary*: High-contrast `on-primary` text on the emerald background or outlined with a hover-glow effect.
    - *Semantic actions*: Solid secondary, warning, error and tertiary surfaces use their corresponding `on-*` foreground token.
    - *Ghost/Tertiary*: Transparent background with `on-surface-variant` text, shifting to `primary` on hover.
- **Status Chips**: Pill-shaped with a 2px inner "LED" dot. The dot should have a `3px` blur shadow of its own color.
- **Data Tables**: Use a zebra-stripe effect with `0.3` opacity on alternating rows. Headers should be sticky with a backdrop-blur.
- **Metric Cards**: Features a top-aligned gradient border (primary to transparent) that only appears on hover to indicate interactivity.
- **Navigation Items**: The active state uses a left-aligned 4px border-accent and a subtle scale-down (95%) to feel "pressed."
- **Alert Boxes**: High-saturation borders with a background tint derived from the `error` color at 10% opacity.
