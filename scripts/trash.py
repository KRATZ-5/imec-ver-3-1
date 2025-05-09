# from fastapi import APIRouter, Request, Depends
# from fastapi.responses import HTMLResponse, RedirectResponse
# from fastapi.templating import Jinja2Templates
# from app.services.consumption_service import load_regions, aggregate_by_region, compute_centroids
# from app.dependencies import get_current_user
#
# router = APIRouter()
# templates = Jinja2Templates(directory="app/templates")
#
# @router.get("/", response_class=HTMLResponse)
# async def index(request: Request, user=Depends(get_current_user)):
#     regions = load_regions()
#     agg = aggregate_by_region()
#     print("=== AGGREGATED CONSUMPTION ===")
#     print(agg)
#     print("Available codes in CSV:", agg["region_code"].tolist())
#     print("=== GEOJSON CODES ===")
#     print([feat["properties"]["code"] for feat in regions["features"]])
#     centroids = compute_centroids(regions)
#     avg_lat = sum(lat for lat,lon in centroids)/len(centroids)
#     avg_lon = sum(lon for lat,lon in centroids)/len(centroids)
#
#     import folium
#     from folium.plugins import HeatMap, Search
#
#     m = folium.Map(location=[avg_lat, avg_lon], zoom_start=6)
#     # ... хлороплет и HeatMap как раньше ...
#     map_html = m._repr_html_()
#     return templates.TemplateResponse("index.html", {
#         "request": request, "map_html": map_html, "user": user
#     })
#
# @router.get("/login", response_class=HTMLResponse)
# async def login_get(request: Request):
#     return templates.TemplateResponse("login.html", {"request": request})
#
# @router.get("/register", response_class=HTMLResponse)
# async def register_get(request: Request):
#     return templates.TemplateResponse("register.html", {"request": request})
#
# @router.get("/logout")
# async def logout():
#     resp = RedirectResponse(url="/login")
#     resp.delete_cookie("token")
#     return resp
