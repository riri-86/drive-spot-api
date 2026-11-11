from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import Literal

from app.database import get_db
from app.models import Route, RouteVia
from app.schemas.route import RouteCreate, RouteRead
from app.services.routes_api import RoutesApiError, fetch_route_steps
from app.services.scoring import curve_deg_per_km_by_steps, detour_ratio, route_length_km

router = APIRouter()


# Google からルートを受け取り、採点する(登録と編集の両方で使う)
def fetch_and_score(route_in: RouteCreate) -> dict:
    origin = (route_in.origin_lat, route_in.destination_lng)
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
        return {
            "length_km": route_length_km(points),
            "detour_ratio": detour_ratio(points),
            "curve_deg_per_km": curve_deg_per_km_by_steps(steps_points),
        }
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    

# ルート登録(Google からルートを受け取り、採点して保存する)
@router.post("/routes", response_model=RouteRead, status_code=201)
def create_route(route_in: RouteCreate, db: Session = Depends(get_db)):
    scores = fetch_and_score(route_in)

    route = Route(
        name=route_in.name,
        origin_lat=route_in.origin_lat,
        origin_lng=route_in.origin_lng,
        destination_lat=route_in.destination_lat,
        destination_lng=route_in.destination_lng,
        **scores,
    )

    for position, via in enumerate(route_in.vias, start=1):
        route.vias.append(RouteVia(position=position, lat=via.lat, lng=via.lng))

    db.add(route)
    db.commit()
    db.refresh(route)
    return route


# ルート一覧を取得
SORT_COLUMNS = {
    "id": Route.id,
    "length_km": Route.length_km,
    "detour_ratio": Route.detour_ratio,
    "curve_deg_per_km": Route.curve_deg_per_km,
}


@router.get("/routes", response_model=list[RouteRead])
def list_routes(
    sort: Literal["id", "length_km", "detour_ratio", "curve_deg_per_km"] = "id",
    order: Literal["asc", "desc"] = "asc",
    db: Session = Depends(get_db),
):
    column = SORT_COLUMNS[sort]
    if order == "desc":
        column = column.desc()
    return db.scalars(select(Route).order_by(column, Route.id)).all()


# ルート1件を取得
@router.get("/routes/{route_id}", response_model=RouteRead)
def get_route(route_id: int, db: Session = Depends(get_db)):
    route = db.get(Route, route_id)
    if route is None:
        raise HTTPException(status_code=404, detail="Route not found")
    return route


# ルート削除
@router.delete("/routes/{route_id}", status_code=204)
def delete_route(route_id: int, db: Session = Depends(get_db)):
    route = db.get(Route, route_id)
    if route is None:
        raise HTTPException(status_code=404, detail="Route not found")

    db.delete(route)
    db.commit()


# 編集(地点が変わった時だけ、Google を呼び直して採点し直す)
@router.put("/routes/{route_id}", response_model=RouteRead)
def update_route(route_id: int, route_in: RouteCreate, db: Session = Depends(get_db)):
    route = db.get(Route, route_id)
    if route is None:
        raise HTTPException(status_code=404, detail="Route not found")

    old_places = (
        (route.origin_lat, route.origin_lng),
        (route.destination_lat, route.destination_lng),
        [(via.lat, via.lng) for via in route.vias],
    )
    new_places = (
        (route_in.origin_lat, route_in.origin_lng),
        (route_in.destination_lat, route_in.destination_lng),
        [(via.lat, via.lng) for via in route_in.vias],
    )

    if new_places != old_places:
        scores = fetch_and_score(route_in)
        for key, value in scores.items():
            setattr(route, key, value)

        route.origin_lat = route_in.origin_lat
        route.origin_lng = route_in.origin_lng
        route.destination_lat = route_in.destination_lat
        route.destination_lng = route_in.destination_lng
        route.vias = [
            RouteVia(position=position, lat=via.lat, lng=via.lng)
            for position, via in enumerate(route_in.vias, start=1)
        ]

    route.name = route_in.name

    db.commit()
    db.refresh(route)
    return route
