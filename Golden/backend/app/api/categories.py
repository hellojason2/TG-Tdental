"""Products, categories, and sources lookup endpoints."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

import psycopg2
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from psycopg2.extras import RealDictCursor

from app.core.database import get_conn
from app.core.lookup_sql import (
    TableRef,
    empty_page,
    page_window,
    pick_column,
    quote_ident,
    resolve_table,
    table_columns,
)
from app.core.middleware import require_auth
from app.core.pagination import paginate

router = APIRouter(prefix="/api", tags=["catalog"])


class CategorySavePayload(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    code: str | None = Field(default=None, max_length=255)
    type: str | None = Field(default=None, max_length=255)
    active: bool | None = None
    companyId: str | None = Field(default=None, max_length=64)


@dataclass()
class ManageSpec:
    key: str
    table_candidates: tuple[str, ...]
    mode: str  # generic | product | doctor


@router.get("/products")
async def list_products(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=0, le=500),
    offset: int | None = Query(default=None, ge=0),
    limit: int | None = Query(default=None, ge=0, le=5000),
    search: str = Query(default=""),
    type: str | None = Query(default=None),
    companyId: str | None = Query(default=None),
    _user: dict = Depends(require_auth),
):
    """Return paginated products/services for shared dropdowns."""
    effective_offset, effective_limit = page_window(
        page=page,
        per_page=per_page,
        offset=offset,
        limit=limit,
        default_limit=20,
    )

    try:
        with get_conn() as conn:
            products_table = resolve_table(conn, "products", "product")
            if not products_table:
                return empty_page(effective_offset, effective_limit)

            product_cols = table_columns(conn, products_table)
            id_col = pick_column(product_cols, "id")
            name_col = pick_column(product_cols, "name", "display_name")
            if not id_col or not name_col:
                return empty_page(effective_offset, effective_limit)

            default_code_col = pick_column(product_cols, "default_code", "defaultcode")
            display_name_col = pick_column(product_cols, "display_name", "displayname")
            list_price_col = pick_column(product_cols, "list_price", "listprice")
            standard_price_col = pick_column(product_cols, "standard_price", "standardprice")
            type_col = pick_column(product_cols, "type")
            type2_col = pick_column(product_cols, "type2")
            company_id_col = pick_column(product_cols, "company_id", "companyid")
            company_name_col = pick_column(product_cols, "company_name", "companyname")
            category_id_col = pick_column(product_cols, "categ_id", "category_id", "categid")
            is_labo_col = pick_column(product_cols, "is_labo", "islabo")
            active_col = pick_column(product_cols, "active", "is_active")

            product_categories_table = resolve_table(
                conn, "product_categories", "productcategories"
            )
            category_join = ""
            category_name_expr = "NULL::text"
            if product_categories_table and category_id_col:
                category_cols = table_columns(conn, product_categories_table)
                pc_id_col = pick_column(category_cols, "id")
                pc_name_col = pick_column(category_cols, "name")
                if pc_id_col and pc_name_col:
                    category_join = (
                        f" LEFT JOIN {product_categories_table.qualified_name} pc"
                        f" ON p.{quote_ident(category_id_col)} = pc.{quote_ident(pc_id_col)}"
                    )
                    category_name_expr = f"pc.{quote_ident(pc_name_col)}"

            select_fields = [
                f'p.{quote_ident(id_col)}::text AS id',
                f'p.{quote_ident(name_col)} AS name',
                (
                    f'p.{quote_ident(display_name_col)} AS "displayName"'
                    if display_name_col
                    else 'NULL::text AS "displayName"'
                ),
                (
                    f'p.{quote_ident(default_code_col)} AS "defaultCode"'
                    if default_code_col
                    else 'NULL::text AS "defaultCode"'
                ),
                (
                    f"COALESCE(p.{quote_ident(list_price_col)}, 0) AS \"listPrice\""
                    if list_price_col
                    else '0::numeric AS "listPrice"'
                ),
                (
                    f"COALESCE(p.{quote_ident(standard_price_col)}, 0) AS \"standardPrice\""
                    if standard_price_col
                    else '0::numeric AS "standardPrice"'
                ),
                (
                    f'p.{quote_ident(type_col)} AS type'
                    if type_col
                    else "NULL::text AS type"
                ),
                (
                    f'p.{quote_ident(type2_col)} AS type2'
                    if type2_col
                    else "NULL::text AS type2"
                ),
                (
                    f'p.{quote_ident(category_id_col)}::text AS "categoryId"'
                    if category_id_col
                    else 'NULL::text AS "categoryId"'
                ),
                f'{category_name_expr} AS "categoryName"',
                (
                    f'p.{quote_ident(company_id_col)}::text AS "companyId"'
                    if company_id_col
                    else 'NULL::text AS "companyId"'
                ),
                (
                    f'p.{quote_ident(company_name_col)} AS "companyName"'
                    if company_name_col
                    else 'NULL::text AS "companyName"'
                ),
                (
                    f'COALESCE(p.{quote_ident(is_labo_col)}, FALSE) AS "isLabo"'
                    if is_labo_col
                    else 'FALSE AS "isLabo"'
                ),
                (
                    f"COALESCE(p.{quote_ident(active_col)}, TRUE) AS active"
                    if active_col
                    else "TRUE AS active"
                ),
            ]

            where_clauses: list[str] = []
            params: list = []

            search_text = search.strip()
            if search_text:
                pattern = f"%{search_text}%"
                search_parts = [f"p.{quote_ident(name_col)} ILIKE %s"]
                params.append(pattern)
                if default_code_col:
                    search_parts.append(f"p.{quote_ident(default_code_col)} ILIKE %s")
                    params.append(pattern)
                if display_name_col:
                    search_parts.append(f"p.{quote_ident(display_name_col)} ILIKE %s")
                    params.append(pattern)
                where_clauses.append(f"({' OR '.join(search_parts)})")

            if type:
                if type_col and type2_col:
                    where_clauses.append(
                        f"(p.{quote_ident(type_col)} = %s OR p.{quote_ident(type2_col)} = %s)"
                    )
                    params.extend([type, type])
                elif type_col:
                    where_clauses.append(f"p.{quote_ident(type_col)} = %s")
                    params.append(type)
                elif type2_col:
                    where_clauses.append(f"p.{quote_ident(type2_col)} = %s")
                    params.append(type)
                else:
                    return empty_page(effective_offset, effective_limit)

            if companyId:
                if company_id_col:
                    where_clauses.append(f"p.{quote_ident(company_id_col)}::text = %s")
                    params.append(companyId)
                else:
                    return empty_page(effective_offset, effective_limit)

            order_col = quote_ident(name_col)
            base_query = (
                f"SELECT {', '.join(select_fields)} "
                f"FROM {products_table.qualified_name} p{category_join}"
            )
            if where_clauses:
                base_query += " WHERE " + " AND ".join(where_clauses)
            base_query += f" ORDER BY p.{order_col} ASC NULLS LAST"

            return paginate(
                query=base_query,
                params=tuple(params),
                conn=conn,
                offset=effective_offset,
                limit=effective_limit,
            )
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


@router.get("/categories/products")
async def list_product_categories(_user: dict = Depends(require_auth)):
    """Return product category tree with parent links."""
    return _list_categories("product_categories", "productcategories")


@router.get("/categories/partners")
async def list_partner_categories(_user: dict = Depends(require_auth)):
    """Return partner/customer categories."""
    return _list_categories("partner_categories", "partnercategories")


@router.get("/sources")
async def list_sources(_user: dict = Depends(require_auth)):
    """Return partner sources list for dropdowns."""
    try:
        with get_conn() as conn:
            source_table = resolve_table(conn, "partner_sources", "partnersources", "sources")
            if not source_table:
                return []

            cols = table_columns(conn, source_table)
            id_col = pick_column(cols, "id")
            name_col = pick_column(cols, "name")
            if not id_col or not name_col:
                return []

            type_col = pick_column(cols, "type")
            is_active_col = pick_column(cols, "is_active", "isactive", "active")

            query = (
                "SELECT "
                f"s.{quote_ident(id_col)}::text AS id, "
                f"s.{quote_ident(name_col)} AS name, "
                + (
                    f"s.{quote_ident(type_col)} AS type, "
                    if type_col
                    else "NULL::text AS type, "
                )
                + (
                    f'COALESCE(s.{quote_ident(is_active_col)}, TRUE) AS "isActive" '
                    if is_active_col
                    else 'TRUE AS "isActive" '
                )
                + f"FROM {source_table.qualified_name} s "
                f"ORDER BY s.{quote_ident(name_col)} ASC NULLS LAST"
            )

            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query)
                rows = cur.fetchall()
            return [dict(row) for row in rows]
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


def _list_categories(*table_candidates: str) -> list[dict]:
    """Read category table and normalise to id/name/parentId shape."""
    try:
        with get_conn() as conn:
            table_ref = resolve_table(conn, *table_candidates)
            if not table_ref:
                return []

            cols = table_columns(conn, table_ref)
            id_col = pick_column(cols, "id")
            name_col = pick_column(cols, "name")
            if not id_col or not name_col:
                return []

            parent_col = pick_column(cols, "parent_id", "parentid")

            query = (
                "SELECT "
                f"c.{quote_ident(id_col)}::text AS id, "
                f"c.{quote_ident(name_col)} AS name, "
                + (
                    f'c.{quote_ident(parent_col)}::text AS "parentId" '
                    if parent_col
                    else 'NULL::text AS "parentId" '
                )
                + f"FROM {table_ref.qualified_name} c "
                f"ORDER BY c.{quote_ident(name_col)} ASC NULLS LAST"
            )

            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query)
                rows = cur.fetchall()
            return [dict(row) for row in rows]
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


_MANAGE_SPECS: dict[str, ManageSpec] = {
    "services": ManageSpec(
        key="services",
        table_candidates=("products", "product"),
        mode="product",
    ),
    "products": ManageSpec(
        key="products",
        table_candidates=("products", "product"),
        mode="product",
    ),
    "doctors": ManageSpec(
        key="doctors",
        table_candidates=("employees", "employee"),
        mode="doctor",
    ),
    "branches": ManageSpec(
        key="branches",
        table_candidates=("companies", "company"),
        mode="generic",
    ),
    "partner-categories": ManageSpec(
        key="partner-categories",
        table_candidates=("partner_categories", "partnercategories"),
        mode="generic",
    ),
    "partner-sources": ManageSpec(
        key="partner-sources",
        table_candidates=("partner_sources", "partnersources", "sources"),
        mode="generic",
    ),
    "card-types": ManageSpec(
        key="card-types",
        table_candidates=("card_types", "cardtypes"),
        mode="generic",
    ),
    # --- Additional category sub-types ---
    "customer-labels": ManageSpec(
        key="customer-labels",
        table_candidates=("customer_labels", "customerlabels"),
        mode="generic",
    ),
    "customer-titles": ManageSpec(
        key="customer-titles",
        table_candidates=("partner_titles", "partnertitles", "res_partner_titles", "respartnertitles"),
        mode="generic",
    ),
    "medical-history": ManageSpec(
        key="medical-history",
        table_candidates=("medical_histories", "medicalhistory", "medical_history", "tiensubenhly"),
        mode="generic",
    ),
    "customer-stages": ManageSpec(
        key="customer-stages",
        table_candidates=("customer_stages", "customerstages", "partner_stages", "partnerstages"),
        mode="generic",
    ),
    "suppliers": ManageSpec(
        key="suppliers",
        table_candidates=("partners", "res_partners", "respartners"),
        mode="generic",
    ),
    "insurance": ManageSpec(
        key="insurance",
        table_candidates=("insurance_companies", "insurancecompanies", "insurance", "bao_hiem"),
        mode="generic",
    ),
    "referrers": ManageSpec(
        key="referrers",
        table_candidates=("partner_sources", "partnersources", "sources", "referrers"),
        mode="generic",
    ),
    "prescriptions": ManageSpec(
        key="prescriptions",
        table_candidates=("prescription_templates", "prescriptiontemplates", "prescriptions", "toa_thuoc"),
        mode="generic",
    ),
    "price-lists": ManageSpec(
        key="price-lists",
        table_candidates=("price_lists", "pricelists", "pricelist", "product_pricelists"),
        mode="generic",
    ),
    "commission-tables": ManageSpec(
        key="commission-tables",
        table_candidates=("commission_tables", "commissiontables", "commission_rates", "commissionrates"),
        mode="generic",
    ),
    "employees": ManageSpec(
        key="employees",
        table_candidates=("employees", "employee"),
        mode="generic",
    ),
    "departments": ManageSpec(
        key="departments",
        table_candidates=("departments", "department", "hr_departments", "hrdepartments"),
        mode="generic",
    ),
    "job-titles": ManageSpec(
        key="job-titles",
        table_candidates=("job_titles", "jobtitles", "hr_jobs", "hrjobs", "hr_job"),
        mode="generic",
    ),
    "labo-materials": ManageSpec(
        key="labo-materials",
        table_candidates=("labo_materials", "labomaterials", "labo_material_types", "labomaterialtypes"),
        mode="generic",
    ),
    "labo-attachments": ManageSpec(
        key="labo-attachments",
        table_candidates=("labo_attachments", "laboattachments", "labo_attachment_types", "laboattachmenttypes"),
        mode="generic",
    ),
    "income-types": ManageSpec(
        key="income-types",
        table_candidates=("income_types", "incometypes", "income_categories", "loai_thu"),
        mode="generic",
    ),
    "expense-types": ManageSpec(
        key="expense-types",
        table_candidates=("expense_types", "expensetypes", "expense_categories", "loai_chi"),
        mode="generic",
    ),
    "stock-criteria": ManageSpec(
        key="stock-criteria",
        table_candidates=("stock_criteria", "stockcriteria", "inventory_criteria", "tieu_chi_kiem_ke"),
        mode="generic",
    ),
    "tooth-diagnosis": ManageSpec(
        key="tooth-diagnosis",
        table_candidates=("tooth_diagnosis", "toothdiagnosis", "dental_diagnosis", "icd10_codes", "diagnosis_codes"),
        mode="generic",
    ),
}

_APP_MANAGE_TABLE_BY_KIND: dict[str, str] = {
    "customer-labels": "app_category_customer_labels",
    "customer-titles": "app_category_customer_titles",
    "medical-history": "app_category_medical_history",
    "customer-stages": "app_category_customer_stages",
    "suppliers": "app_category_suppliers",
    "insurance": "app_category_insurance",
    "referrers": "app_category_referrers",
    "prescriptions": "app_category_prescriptions",
    "price-lists": "app_category_price_lists",
    "commission-tables": "app_category_commission_tables",
    "departments": "app_category_departments",
    "job-titles": "app_category_job_titles",
    "labo-materials": "app_category_labo_materials",
    "labo-attachments": "app_category_labo_attachments",
    "income-types": "app_category_income_types",
    "expense-types": "app_category_expense_types",
    "stock-criteria": "app_category_stock_criteria",
    "tooth-diagnosis": "app_category_tooth_diagnosis",
}


def _ensure_app_manage_table(conn, table_name: str) -> TableRef:
    with conn.cursor() as cur:
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS public.{quote_ident(table_name)} (
                id UUID PRIMARY KEY,
                name TEXT NOT NULL,
                code TEXT,
                type TEXT,
                active BOOLEAN NOT NULL DEFAULT TRUE,
                company_id UUID,
                company_name TEXT,
                updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
            );
            """
        )
        cur.execute(
            f"""
            CREATE INDEX IF NOT EXISTS idx_{table_name}_name
            ON public.{quote_ident(table_name)} (name);
            """
        )
        cur.execute(
            f"""
            CREATE INDEX IF NOT EXISTS idx_{table_name}_active
            ON public.{quote_ident(table_name)} (active);
            """
        )
        cur.execute(
            f"""
            CREATE INDEX IF NOT EXISTS idx_{table_name}_company_id
            ON public.{quote_ident(table_name)} (company_id);
            """
        )
    return TableRef(schema="public", table=table_name)


def _normalise_manage_kind(kind: str) -> ManageSpec:
    key = (kind or "").strip().lower()
    spec = _MANAGE_SPECS.get(key)
    if not spec:
        raise HTTPException(status_code=404, detail="Category type is not supported")
    return spec


def _table_column_data_types(conn, table_ref) -> dict[str, str]:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT lower(column_name), lower(data_type)
            FROM information_schema.columns
            WHERE table_schema = %s
              AND table_name = %s
            """,
            (table_ref.schema, table_ref.table),
        )
        rows = cur.fetchall()
    return {row[0]: row[1] for row in rows}


def _resolve_manage_table(conn, candidates: tuple[str, ...]) -> TableRef | None:
    """Resolve manage table using candidate priority order."""
    for candidate in candidates:
        table_ref = resolve_table(conn, candidate)
        if table_ref:
            return table_ref
    return None


def _manage_context(conn, spec: ManageSpec) -> dict | None:
    table = _resolve_manage_table(conn, spec.table_candidates)
    if not table:
        fallback_table = _APP_MANAGE_TABLE_BY_KIND.get(spec.key)
        if fallback_table:
            table = _ensure_app_manage_table(conn, fallback_table)
    if not table:
        return None

    cols = table_columns(conn, table)
    id_col = pick_column(cols, "id")
    name_col = pick_column(cols, "name", "display_name")
    if not id_col or not name_col:
        return None

    context = {
        "table": table,
        "cols": cols,
        "id_col": id_col,
        "name_col": name_col,
        "code_col": pick_column(cols, "code", "default_code", "ref"),
        "type_col": pick_column(cols, "type", "type2"),
        "active_col": pick_column(cols, "active", "is_active", "isactive"),
        "company_id_col": pick_column(cols, "company_id", "companyid"),
        "company_name_col": pick_column(cols, "company_name", "companyname"),
        "updated_col": pick_column(cols, "updated_at", "updatedon", "write_date"),
        "job_col": pick_column(cols, "hr_job", "job_name", "job"),
        "is_doctor_col": pick_column(cols, "is_doctor", "isdoctor"),
        "column_types": _table_column_data_types(conn, table),
        "mode": spec.mode,
        "key": spec.key,
    }
    return context


def _manage_filters(context: dict, spec: ManageSpec, search: str, company_id: str | None) -> tuple[list[str], list]:
    where: list[str] = []
    params: list = []

    name_col = context["name_col"]
    search_text = search.strip()
    if search_text:
        pattern = f"%{search_text}%"
        where.append(f"t.{quote_ident(name_col)} ILIKE %s")
        params.append(pattern)

    company_col = context.get("company_id_col")
    if company_id:
        if company_col:
            where.append(f"t.{quote_ident(company_col)}::text = %s")
            params.append(company_id)
        else:
            where.append("1 = 0")

    if spec.mode == "product":
        type_col = context.get("type_col")
        if not type_col:
            where.append("1 = 0")
        else:
            normalized = "LOWER(COALESCE(t." + quote_ident(type_col) + "::text, ''))"
            service_pred = (
                f"({normalized} IN ('service', 'dịch vụ', 'dv') OR {normalized} LIKE '%%service%%')"
            )
            if spec.key == "services":
                where.append(service_pred)
            else:
                where.append(f"NOT {service_pred}")

    if spec.mode == "doctor":
        is_doctor_col = context.get("is_doctor_col")
        if is_doctor_col:
            where.append(f"COALESCE(t.{quote_ident(is_doctor_col)}, FALSE) = TRUE")
        else:
            where.append("1 = 0")

    return where, params


@router.get("/categories/manage/{kind}")
async def list_manage_categories(
    kind: str,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=0, le=500),
    offset: int | None = Query(default=None, ge=0),
    limit: int | None = Query(default=None, ge=0, le=5000),
    search: str = Query(default=""),
    companyId: str | None = Query(default=None),
    _user: dict = Depends(require_auth),
):
    spec = _normalise_manage_kind(kind)
    resolved_offset, resolved_limit = page_window(
        page=page,
        per_page=per_page,
        offset=offset,
        limit=limit,
        default_limit=20,
    )

    try:
        with get_conn() as conn:
            context = _manage_context(conn, spec)
            if not context:
                return empty_page(resolved_offset, resolved_limit)

            where, params = _manage_filters(context, spec, search, companyId)
            where_sql = ""
            if where:
                where_sql = " WHERE " + " AND ".join(where)

            select_fields = [
                f't.{quote_ident(context["id_col"])}::text AS id',
                f't.{quote_ident(context["name_col"])} AS name',
                (
                    f't.{quote_ident(context["code_col"])} AS code'
                    if context.get("code_col")
                    else "NULL::text AS code"
                ),
                (
                    f't.{quote_ident(context["type_col"])} AS type'
                    if context.get("type_col")
                    else "NULL::text AS type"
                ),
                (
                    f'COALESCE(t.{quote_ident(context["active_col"])}, TRUE) AS active'
                    if context.get("active_col")
                    else "TRUE AS active"
                ),
                (
                    f't.{quote_ident(context["company_id_col"])}::text AS "companyId"'
                    if context.get("company_id_col")
                    else 'NULL::text AS "companyId"'
                ),
                (
                    f't.{quote_ident(context["company_name_col"])} AS "companyName"'
                    if context.get("company_name_col")
                    else 'NULL::text AS "companyName"'
                ),
                (
                    f't.{quote_ident(context["job_col"])} AS "jobTitle"'
                    if context.get("job_col")
                    else 'NULL::text AS "jobTitle"'
                ),
                (
                    f't.{quote_ident(context["updated_col"])} AS "updatedAt"'
                    if context.get("updated_col")
                    else "NULL::timestamp AS \"updatedAt\""
                ),
            ]
            query = (
                f"SELECT {', '.join(select_fields)} "
                f"FROM {context['table'].qualified_name} t"
                f"{where_sql} "
                f"ORDER BY t.{quote_ident(context['name_col'])} ASC NULLS LAST"
            )
            return paginate(
                query=query,
                params=tuple(params),
                conn=conn,
                offset=resolved_offset,
                limit=resolved_limit,
            )
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


@router.post("/categories/manage/{kind}", status_code=201)
async def create_manage_category(
    kind: str,
    body: CategorySavePayload,
    _user: dict = Depends(require_auth),
):
    spec = _normalise_manage_kind(kind)

    try:
        with get_conn() as conn:
            context = _manage_context(conn, spec)
            if not context:
                raise HTTPException(status_code=404, detail="Category table is unavailable")

            data = _payload_to_record(context, spec, body, creating=True)
            if not data:
                raise HTTPException(status_code=422, detail="No data to insert")

            columns = list(data.keys())
            placeholders = ", ".join(["%s"] * len(columns))
            query = (
                f"INSERT INTO {context['table'].qualified_name} "
                f"({', '.join(quote_ident(col) for col in columns)}) "
                f"VALUES ({placeholders}) "
                f"RETURNING {quote_ident(context['id_col'])}::text"
            )
            with conn.cursor() as cur:
                cur.execute(query, tuple(data[col] for col in columns))
                row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=500, detail="Insert failed")
            return _fetch_manage_item(conn, context, str(row[0]))
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")
    except HTTPException:
        raise
    except psycopg2.Error as exc:
        raise HTTPException(status_code=400, detail=str(exc).splitlines()[0])


@router.put("/categories/manage/{kind}/{item_id}")
async def update_manage_category(
    kind: str,
    item_id: str,
    body: CategorySavePayload,
    _user: dict = Depends(require_auth),
):
    spec = _normalise_manage_kind(kind)

    try:
        with get_conn() as conn:
            context = _manage_context(conn, spec)
            if not context:
                raise HTTPException(status_code=404, detail="Category table is unavailable")

            data = _payload_to_record(context, spec, body, creating=False)
            if not data:
                raise HTTPException(status_code=422, detail="No data to update")

            set_sql = ", ".join(f"{quote_ident(col)} = %s" for col in data.keys())
            query = (
                f"UPDATE {context['table'].qualified_name} "
                f"SET {set_sql} "
                f"WHERE {quote_ident(context['id_col'])}::text = %s "
                f"RETURNING {quote_ident(context['id_col'])}::text"
            )
            with conn.cursor() as cur:
                cur.execute(query, (*data.values(), item_id))
                row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Item not found")
            return _fetch_manage_item(conn, context, item_id)
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")
    except HTTPException:
        raise
    except psycopg2.Error as exc:
        raise HTTPException(status_code=400, detail=str(exc).splitlines()[0])


@router.delete("/categories/manage/{kind}/{item_id}")
async def delete_manage_category(
    kind: str,
    item_id: str,
    _user: dict = Depends(require_auth),
):
    spec = _normalise_manage_kind(kind)

    try:
        with get_conn() as conn:
            context = _manage_context(conn, spec)
            if not context:
                raise HTTPException(status_code=404, detail="Category table is unavailable")

            query = (
                f"DELETE FROM {context['table'].qualified_name} "
                f"WHERE {quote_ident(context['id_col'])}::text = %s "
                f"RETURNING {quote_ident(context['id_col'])}::text"
            )
            with conn.cursor() as cur:
                cur.execute(query, (item_id,))
                row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Item not found")
            return {"id": str(row[0]), "deleted": True}
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


def _payload_to_record(context: dict, spec: ManageSpec, body: CategorySavePayload, *, creating: bool) -> dict[str, object]:
    data: dict[str, object] = {}
    id_col = context["id_col"]
    column_types = context.get("column_types") or {}

    if creating:
        id_type = (column_types.get(id_col) or "").lower()
        if id_type in {"uuid", "character varying", "varchar", "text"}:
            data[id_col] = str(uuid4())

    data[context["name_col"]] = body.name.strip()

    code_col = context.get("code_col")
    if code_col and body.code is not None:
        data[code_col] = body.code.strip() or None

    type_col = context.get("type_col")
    if type_col:
        if body.type is not None:
            data[type_col] = body.type.strip() or None
        elif creating and spec.mode == "product":
            data[type_col] = "service" if spec.key == "services" else "product"

    active_col = context.get("active_col")
    if active_col and body.active is not None:
        data[active_col] = bool(body.active)
    elif active_col and creating:
        data[active_col] = True

    company_col = context.get("company_id_col")
    if company_col and body.companyId is not None:
        data[company_col] = body.companyId.strip() or None

    if not creating:
        # Never allow id overwrite on update.
        data.pop(id_col, None)

    return data


def _fetch_manage_item(conn, context: dict, item_id: str) -> dict:
    query = (
        "SELECT "
        f't.{quote_ident(context["id_col"])}::text AS id, '
        f't.{quote_ident(context["name_col"])} AS name, '
        + (
            f't.{quote_ident(context["code_col"])} AS code, '
            if context.get("code_col")
            else "NULL::text AS code, "
        )
        + (
            f't.{quote_ident(context["type_col"])} AS type, '
            if context.get("type_col")
            else "NULL::text AS type, "
        )
        + (
            f'COALESCE(t.{quote_ident(context["active_col"])}, TRUE) AS active, '
            if context.get("active_col")
            else "TRUE AS active, "
        )
        + (
            f't.{quote_ident(context["company_id_col"])}::text AS "companyId", '
            if context.get("company_id_col")
            else 'NULL::text AS "companyId", '
        )
        + (
            f't.{quote_ident(context["company_name_col"])} AS "companyName", '
            if context.get("company_name_col")
            else 'NULL::text AS "companyName", '
        )
        + (
            f't.{quote_ident(context["updated_col"])} AS "updatedAt" '
            if context.get("updated_col")
            else 'NULL::timestamp AS "updatedAt" '
        )
        + f"FROM {context['table'].qualified_name} t "
        f"WHERE t.{quote_ident(context['id_col'])}::text = %s "
        "LIMIT 1"
    )
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(query, (item_id,))
        row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Item not found")
    return dict(row)
