---
name: Emerald Operations
colors:
  surface: '#0b1326'
  surface-dim: '#0b1326'
  surface-bright: '#31394d'
  surface-container-lowest: '#060e20'
  surface-container-low: '#131b2e'
  surface-container: '#171f33'
  surface-container-high: '#222a3d'
  surface-container-highest: '#2d3449'
  on-surface: '#dae2fd'
  on-surface-variant: '#bbcabf'
  inverse-surface: '#dae2fd'
  inverse-on-surface: '#283044'
  outline: '#86948a'
  outline-variant: '#3c4a42'
  surface-tint: '#4edea3'
  primary: '#4edea3'
  on-primary: '#003824'
  primary-container: '#10b981'
  on-primary-container: '#00422b'
  inverse-primary: '#006c49'
  secondary: '#95d3ba'
  on-secondary: '#003829'
  secondary-container: '#115340'
  on-secondary-container: '#87c5ac'
  tertiary: '#ffb2b7'
  on-tertiary: '#67011c'
  tertiary-container: '#ff7886'
  on-tertiary-container: '#740c23'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#6ffbbe'
  primary-fixed-dim: '#4edea3'
  on-primary-fixed: '#002113'
  on-primary-fixed-variant: '#005236'
  secondary-fixed: '#b1f0d6'
  secondary-fixed-dim: '#95d3ba'
  on-secondary-fixed: '#002117'
  on-secondary-fixed-variant: '#0d503e'
  tertiary-fixed: '#ffdadb'
  tertiary-fixed-dim: '#ffb2b7'
  on-tertiary-fixed: '#40000e'
  on-tertiary-fixed-variant: '#871d30'
  background: '#0b1326'
  on-background: '#dae2fd'
  surface-variant: '#2d3449'
  surface-main: '#090E0B'
  surface-card: '#141C17'
  surface-border: '#222D26'
  alert-bg: '#1C1315'
  alert-border: '#4A1D24'
  alert-text: '#FFB4AB'
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
  sidebar-width: 260px
  stack-sm: 8px
  stack-md: 16px
  stack-lg: 24px
---

## Brand & Style
The brand identity is rooted in industrial precision and operational efficiency. It targets technical administrators and logistics managers who require high-density data visualization and clear status indicators.

The design style is **Corporate Modern** with a strong emphasis on **Tonal Layering**. It utilizes a deep emerald and slate palette to reduce eye strain during long-term monitoring. The aesthetic is utilitarian yet refined, employing subtle borders and high-contrast typography to create a sense of organized complexity. The UI should feel reliable, high-tech, and structurally sound.

## Colors
The color system uses a "Fidelity" logic where the primary emerald green (#10b981) acts as the functional pulse of the application, signifying activity and online status.

- **Primary**: Emerald Green, used for active states, key icons, and primary accents.
- **Surface Strategy**: A multi-step dark scale starting from a near-black background (#090E0B) moving into deep forest-toned containers (#141C17).
- **Functional Red**: A specialized palette for "Alertas Operativas" using a desaturated deep burgundy background with high-vibrancy coral text to ensure critical visibility without causing visual fatigue.
- **State Indicators**: Use glowing box-shadows (primary/50) for "En Linea" states to simulate physical LED indicators.

## Typography
The system relies exclusively on **Inter** to maintain a neutral, systematic, and highly legible appearance across data-dense tables and technical labels. 

- **Hierarchy**: Emphasized through heavy weight shifts (Extrabold for titles, SemiBold for labels) rather than just size.
- **Labels**: Small caps or uppercase transformations are used for section headers to evoke an industrial dashboard feel.
- **Density**: Line heights are kept tight (1.2 to 1.5) to maximize vertical information density.

## Layout & Spacing
The layout follows a **Fixed-Sidebar Fluid-Canvas** model. 

- **Sidebar**: Fixed at 260px, utilizing a vertical stack for navigation. 
- **Grid**: A standard 12-column system is used within the main canvas, but components primarily organize into 1, 2, or 4 column spans depending on screen width.
- **Breakpoints**: 
    - **Mobile (<768px)**: Sidebar hidden (hamburger menu required), 16px margins, single-column cards.
    - **Tablet (768px - 1280px)**: Sidebar visible, 2-column metric grid.
    - **Desktop (>1280px)**: 4-column metrics, 2:1 ratio for main content vs. sidebar utility panels.
- **Rhythm**: Spacing is strictly based on a 4px baseline unit.

## Elevation & Depth
Depth is achieved through **Tonal Layering** and **Subtle Outlines** rather than heavy shadows.

- **Background**: The lowest level is the `#090E0B` canvas.
- **Surface**: Cards and containers use `#141C17` with a 1px border of `#222D26` to define boundaries.
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
    - *Primary*: High-contrast text on primary background or outlined with a hover-glow effect.
    - *Ghost/Tertiary*: Transparent background with `on-surface-variant` text, shifting to `primary` on hover.
- **Status Chips**: Pill-shaped with a 2px inner "LED" dot. The dot should have a `3px` blur shadow of its own color.
- **Data Tables**: Use a zebra-stripe effect with `0.3` opacity on alternating rows. Headers should be sticky with a backdrop-blur.
- **Metric Cards**: Features a top-aligned gradient border (primary to transparent) that only appears on hover to indicate interactivity.
- **Navigation Items**: The active state uses a left-aligned 4px border-accent and a subtle scale-down (95%) to feel "pressed."
- **Alert Boxes**: High-saturation borders with a background tint derived from the `error` color at 10% opacity.