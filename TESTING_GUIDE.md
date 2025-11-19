# Testing Guide: Frontend & Backend Enhancements

## Quick Start

### 1. Start Backend
```bash
cd backend
python main.py
```

Expected output:
```
============================================================
LOCALENS API STARTUP
============================================================
LLM Provider: OpenRouter (key configured: True)
HERE Maps API: Configured
Embedding Model: sentence-transformers/all-MiniLM-L6-v2
Port: 8000
============================================================
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. Start Frontend
```bash
cd frontend
npm run dev
```

Expected output:
```
VITE v5.4.21  ready in 1000 ms
➜  Local:   http://127.0.0.1:5173/
```

### 3. Test Basic Flow

#### Visit Home Page
- http://127.0.0.1:5173/
- Should show warm, earthy design with addon checkboxes
- All addons should be checked by default

#### Submit Test Address
Paste this address:
```
Flat 202, Tower B, Prestige Tech Park, Marathahalli, Bangalore 560037
```

Click "Process Address" (terracotta button)

#### Expected Results Page

**Top Section:**
1. ✅ Spatial Health Tag (HIGH/MEDIUM/LOW confidence badge)
2. ✅ Geospatial Insights Summary (warm gradient card with confidence level)
3. ⚠️  Anomaly Banner (if any detected - yellow background)

**Main Content:**
4. ✅ Cleaned Address Card (with component chips)
5. ✅ **Interactive Map** with HERE pin (mint) and ML pin (sky blue)
   - Dashed line connecting pins
   - Confidence circle around HERE pin
   - Distance badge at bottom
6. ✅ Three-column grid:
   - Integrity meter (left)
   - Confidence meter (left)
   - Administrative Hierarchy card (middle - may show "Not available" for some fields)
   - Radar Chart (right - 4 axes)
7. ✅ ML vs HERE Comparison (side-by-side panels)
8. ✅ Timeline (vertical processing steps)
9. ✅ 5 Addon Cards Grid:
   - Deliverability
   - Property Risk
   - Fraud
   - Neighborhood
   - Consensus

**Bottom:**
10. ✅ "Check Another Address" button

---

## Validation Checklist

### Visual Tests

#### Home Page
- [ ] Inter font loaded
- [ ] Warm beige background (#FAFAF8)
- [ ] 5 addon checkboxes visible
- [ ] Checkboxes have descriptions
- [ ] Terracotta button on hover effect

#### Results Page - Layout
- [ ] Consistent 32px spacing between sections
- [ ] All cards have rounded-xl corners
- [ ] Shadow-sm on all cards
- [ ] Responsive grid on different screen sizes

#### Results Page - New Components
- [ ] **MapPanel**: Dual pins visible, dashed line, distance badge
- [ ] **GeospatialInsightsSummary**: Summary text generated, confidence badge present
- [ ] **AdministrativeHierarchy**: At least some fields populated (or graceful "N/A")
- [ ] **RadarChart**: 4-axis chart visible, colored by score
- [ ] **MLvsHEREComparison**: Two panels side-by-side, blue vs green theme
- [ ] **SpatialHealthTag**: Colored badge with description
- [ ] **Timeline**: Processing steps listed vertically

### Functional Tests

#### Backend API
- [ ] `/health` returns 200 OK
- [ ] `/process_v3` (no addons) returns cleaned address
- [ ] `/process_v3?addons=all` returns all 5 addons
- [ ] Response includes `trace` array (optional)
- [ ] Response includes `summary.human_readable` (optional)
- [ ] `integrity.components` includes admin fields when available

Run compatibility test:
```bash
cd backend
python ../test_backend_compatibility.py
```

Expected output:
```
✓ Health: { "status": "ok" }
✓ All required fields present
✓ New trace field: Present
✓ New summary field: Present
✓ deliverability: ['deliverability_score', ...]
✓ property_risk: ['risk_score', ...]
Tests passed: 3/3
✓ All tests passed - Backend is backwards-compatible!
```

#### Frontend Data Flow
- [ ] Submitting address navigates to `/results`
- [ ] Results page receives `event` data
- [ ] MapPanel extracts coordinates correctly
- [ ] Timeline displays if `event.trace` exists
- [ ] Components handle missing data without errors

### Browser Console Checks

**No Errors Expected:**
- TypeScript compilation errors
- React rendering errors
- Missing prop warnings
- HERE Maps script errors

**Warnings OK:**
- Deprecation warnings from libraries
- Development mode warnings

---

## Common Issues & Solutions

### Issue: MapPanel shows "No coordinates available"
**Cause:** HERE geocoding failed or API key invalid  
**Solution:** 
1. Check `backend/.env` has valid `HERE_API_KEY`
2. Check backend logs for "HERE GEOCODER" messages
3. Try different address

### Issue: Administrative Hierarchy shows "Not available"
**Cause:** HERE response doesn't include admin fields  
**Solution:** This is normal for some addresses - component works correctly

### Issue: Timeline shows only 2-3 steps
**Cause:** Backend `trace` field may be minimal  
**Solution:** Check if `event.trace` exists in API response - this is optional

### Issue: Radar Chart shows all 0%
**Cause:** Geospatial checks failed  
**Solution:** Check `event.geospatial_checks` in API response

### Issue: Map pins don't show
**Cause:** HERE Maps SDK not loaded  
**Solution:** 
1. Check browser console for script errors
2. Verify HERE API key is valid
3. Check network tab for 403/401 errors

---

## Performance Benchmarks

### Backend Response Times
- **Without addons**: 500-1500ms (first call includes model warmup)
- **With all addons**: 1000-2500ms
- **Cached result**: <50ms

### Frontend Render Times
- **Initial page load**: <2s
- **Results page render**: <500ms
- **Map initialization**: 1-2s (HERE SDK load)

---

## Data Validation Tests

### Test Case 1: Valid Address
```
Input: "123 MG Road, Bengaluru 560001"
Expected:
- Integrity: >80%
- HERE confidence: >90%
- ML similarity: >85%
- City match: ✓
- Pincode match: ✓
- Health: OK
- Distance: <3km (HIGH confidence)
```

### Test Case 2: Incomplete Address
```
Input: "Bangalore"
Expected:
- Integrity: 30-50%
- HERE confidence: 60-80%
- Health: UNCERTAIN or BAD
- Administrative hierarchy may be present
```

### Test Case 3: Invalid Address
```
Input: "asdfghjkl"
Expected:
- Low confidence scores
- Anomaly detected
- Health: BAD
- Self-heal attempted
```

---

## Backwards Compatibility Verification

### Old API Clients
Test that old clients still work:

```python
import requests

# Old-style request (should still work)
response = requests.post("http://127.0.0.1:8000/process_v3", json={
    "raw_address": "Test address"
})

event = response.json()["event"]

# Check all old fields exist
assert "cleaned" in event or "cleaned_address" in event
assert "integrity" in event
assert "ml_results" in event
assert "here_results" in event
assert "health" in event

# New fields are optional - clients can ignore them
print("✓ Backwards compatibility verified")
```

---

## Deployment Checklist

Before deploying to production:

### Frontend
- [ ] Run `npm run build` successfully
- [ ] Check bundle size (<2MB)
- [ ] Test on Chrome, Firefox, Safari
- [ ] Test on mobile devices
- [ ] Verify HERE API key environment variable

### Backend
- [ ] All tests pass
- [ ] Environment variables configured
- [ ] CORS settings appropriate for production
- [ ] Rate limiting configured (if needed)
- [ ] Logging configured correctly

### Documentation
- [ ] ENHANCEMENT_SUMMARY.md reviewed
- [ ] API documentation updated (if changed)
- [ ] Component README.md accurate
- [ ] Test coverage documented

---

## Rollback Plan

If issues occur:

### Frontend Rollback
```bash
cd frontend
git checkout HEAD~1 src/pages/Results.tsx
git checkout HEAD~1 src/components/geo/
git checkout HEAD~1 src/api/client.ts
git checkout HEAD~1 src/index.css
npm run dev
```

### Backend Rollback
```bash
cd backend
git checkout HEAD~1 main.py
python main.py
```

**Note:** New optional fields won't break old frontend versions - they'll simply ignore the extra data.

---

## Success Criteria

✅ **All tests pass**  
✅ **No TypeScript errors**  
✅ **No console errors in browser**  
✅ **Responsive on mobile/tablet/desktop**  
✅ **All 7 new components render**  
✅ **Backwards compatibility maintained**  
✅ **Performance acceptable (<2s load time)**  
✅ **Professional design applied throughout**  

---

## Support

If you encounter issues:
1. Check browser console for errors
2. Review backend logs
3. Run `test_backend_compatibility.py`
4. Verify environment variables
5. Check ENHANCEMENT_SUMMARY.md for implementation details
