# Design Guide

## Colors

**Primary**
- Starbucks Green: #00704A
- Dark Green: #005031
- Light Green: #D4E9E2
- Cream: #F7F7F7
- White: #FFFFFF

**Accents**
- Gold: #FFD700 (Splurge)
- Success: #00A862
- Error: #D62B1F

## Layout

**Navigation**
Sticky white bar with logo, links, and sign in button

**Hero**
Dark green gradient with title and "Get Started" button

**Recommendation Page**
- Mood buttons (Happy, Tired, Stressed, Focused)
- Budget progress bar with color indicators
- Budget input with "Can I Splurge?" button
- Top 3 drink cards with rankings and match scores
- "Order Now" buttons

**Budget Progress Bar**
- Green: <60% spent
- Orange: 60-80% spent
- Red: >80% spent

**Drink Cards**
Name, price, category, ranking badge, match score, mood tags, order button

**Menu Page**
Category filters, grid of drink cards

**Profile**
User info, budget settings, purchase history

**Auth Modal**
Username/password fields, sign in button, sign up link

## Components

**Buttons**
- Primary: Green for main actions
- Splurge: Gold with sparkle
- Filters: Outlined, fills when active

**Mood Buttons**
- Default: Light green
- Selected: Dark green + white text
- Hover: Lift animation

**Cards**
White, 12px rounded, shadow on hover

**Toast Notifications**
Bottom-right, auto-dismiss after 3 seconds

## Typography

- Font: Segoe UI, sans-serif
- Base: 16px, line-height 1.6
- Headings: 48px / 40px / 29px / 21px
- Weights: 400 (regular), 600 (semibold), 700 (bold)

## Spacing

Sections: 64px, Cards: 32px, Elements: 16px

## Responsive

- Desktop (>768px): 3-column grid, full nav
- Mobile (≤768px): 1-column, stacked buttons

## Animations

- Hover/fade: 0.3s
- Progress bar: 0.5s
- Loading: Rotating spinner

## Principles

- Clean, minimal design with white space
- Card-based layout
- Starbucks green for CTAs
- Clear hierarchy
- Hover states and feedback
- High contrast, accessible

## Brand

Starbucks green (#00704A), cream backgrounds, rounded corners, premium feel