# School Directory - Floor Plan Setup Guide

## How to Use Your School Floor Plan Image

The directory now supports using an actual school floor plan image, similar to how malls display their directory maps.

### Step 1: Add Your Floor Plan Images

1. Place your school floor plan images in the `static/images/` directory
2. Name them according to the floor number:
   - `floor_plan_floor_1.png` (for Floor 1)
   - `floor_plan_floor_2.png` (for Floor 2)
   - `floor_plan_floor_3.png` (for Floor 3)
   - etc.

   Or use a single image for all floors:
   - `floor_plan.png` (will be used for all floors)

**Note**: PNG format is recommended for better quality, especially for floor plans with text and lines. The system supports PNG, JPG, and WebP formats.

### Step 2: Adjust Zone Overlays

The zone overlays (clickable areas) are positioned using percentage values. Edit the HTML in `templates/directory.html` to match your floor plan:

1. Find the overlay zones section (around line 332)
2. Adjust the `left`, `top`, `width`, and `height` percentage values to match your floor plan layout
3. Example:
   ```html
   <div class="map-zone ..." 
        style="left: 10%; top: 15%; width: 20%; height: 25%;">
   ```
   - `left: 10%` = 10% from the left edge
   - `top: 15%` = 15% from the top edge
   - `width: 20%` = zone width is 20% of the image width
   - `height: 25%` = zone height is 25% of the image height

### Step 3: Position Facility Markers

Facility markers use the `map_x` and `map_y` fields in the database (as percentages):

- `map_x: 25` = 25% from the left edge of the image
- `map_y: 30` = 30% from the top edge of the image

When adding facilities to the database, set these coordinates to match their location on your floor plan image.

### Step 4: Configure GPS Location (Optional)

The directory now supports GPS-based location tracking! To enable this feature:

1. **Get your school's GPS coordinates** from Google Maps:
   - Right-click on the northwest corner of your school → Select coordinates
   - Right-click on the southeast corner → Select coordinates
   - Or use the bounds from Google Maps API

2. **Update GPS bounds** in `templates/directory.html` (around line 862):
   ```javascript
   const SCHOOL_GPS_BOUNDS = {
     north: 3.0850,  // Northernmost latitude
     south: 3.0840,  // Southernmost latitude
     east: 101.6500,  // Easternmost longitude
     west: 101.6490   // Westernmost longitude
   };
   ```

3. **How it works**:
   - Users click "Show My Location" button
   - Browser requests location permission
   - GPS coordinates are converted to map coordinates
   - A red "You Are Here" marker appears on the map

**Note**: GPS works best outdoors. For indoor navigation, consider:
- WiFi positioning (requires WiFi access point mapping)
- Bluetooth beacons (requires beacon hardware installation)
- Manual zone selection (users select their zone manually)

### Step 5: Position "You Are Here" Marker (Manual)

If you're not using GPS, you can manually position the "You Are Here" marker at:
- `left: 15%`
- `top: 88%`

Adjust these values in the HTML (around line 452) to match your floor plan.

### Tips

- Use high-resolution images (at least 1200px wide) for best quality
- Keep the aspect ratio consistent across all floor images
- Test the clickable zones by hovering over them - they should highlight
- Zones are hidden by default and appear on hover or when clicked
- If the image doesn't load, the SVG placeholder map will be shown instead

### Supported Image Formats

- **PNG** (Recommended) - Best quality for floor plans with text, lines, and diagrams
- JPG/JPEG - Good for photos, but may compress text/details
- WebP - Modern format with good compression

**Default Format**: The system now uses PNG format by default. Place your floor plan images as:
- `floor_plan.png` (single image for all floors)
- `floor_plan_floor_1.png`, `floor_plan_floor_2.png`, etc. (per-floor images)

Make sure your images are optimized for web use to ensure fast loading times.

