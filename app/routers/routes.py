from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Route, RouteVia
from app.schemas.route import RouteCreate, RouteRead
from app.services.routes_api import RoutesApiError, fetch_route_steps
from app.services.scoring import curve_deg_per_km_by_steps, detour_ratio, route_length_km

router = APIRouter()


# ルート登録(Google からルートを受け取り、採点して保存する)
@router.post("/routes", response_model=RouteRead, status_code=201)
def create_route(route_in: RouteCreate, db: Session = Depends(get_db)):
    origin = (route_in.origin_lat, route_in.origin_lng)
    destination = (route_in.destination_lat, route_in.destination_lng)
    vias = []
    for via in route_in.vias:
        vias.append((via.lat, via.lng))

    try:
        steps_points = fetch_route_steps(origin, destination, vias)
    except RoutesApiError as e:
        raise HTTPException(status_code=502, detail=str(e))

    points = []
    for step in steps_points:
        points.extend(step)

    try:
        route = Route(
            name=route_in.name,
            origin_lat=route_in.origin_lat,
            origin_lng=route_in.origin_lng,
            destination_lat=route_in.destination_lat,
            destination_lng=route_in.destination_lng,
            length_km=route_length_km(points),
            detour_ratio=detour_ratio(points),
            curve_deg_per_km=curve_deg_per_km_by_steps(steps_points),
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    for position, via in enumerate(route_in.vias, start=1):
        route.vias.append(RouteVia(position=position, lat=via.lat, lng=via.lng))

    db.add(route)
    db.commit()
    db.refresh(route)
    return route


# ルート一覧を取得
@router.get("/routes", response_model=list[RouteRead])
def list_routes(db: Session = Depends(get_db)):
    return db.scalars(select(Route).order_by(Route.id)).all()


# ルート1件を取得
@router.get("/routes/{route_id}", response_model=RouteRead)
def get_route(route_id: int, db: Session = Depends(get_db)):
    route = db.get(Route, route_id)
    if route is None:
        raise HTTPException(status_code=404, detail="Route not found")
    return route
