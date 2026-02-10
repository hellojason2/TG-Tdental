from datetime import datetime, date
import decimal

def serialize(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    if isinstance(obj, dict):
        return {k: serialize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [serialize(i) for i in obj]
    return obj

def paginate_query(cur, table, select_cols, where="", params=None, sort_col="id", sort_dir="DESC", page=1, per_page=20):
    params = params or []
    cur.execute(f"SELECT COUNT(*) as total FROM {table} {where}", params)
    total = cur.fetchone()["total"]
    offset = (page - 1) * per_page
    cur.execute(f"SELECT {select_cols} FROM {table} {where} ORDER BY {sort_col} {sort_dir} NULLS LAST LIMIT %s OFFSET %s",
                params + [per_page, offset])
    rows = [serialize(dict(row)) for row in cur.fetchall()]
    return {"total": total, "page": page, "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page, "items": rows}

def gen_ref(cur, prefix="KH"):
    """Auto-generate next customer ref like KH000124"""
    cur.execute("SELECT ref FROM customers WHERE ref LIKE %s ORDER BY ref DESC LIMIT 1", [f"{prefix}%"])
    row = cur.fetchone()
    if row and row["ref"]:
        try:
            num = int(row["ref"].replace(prefix, "")) + 1
        except:
            num = 1
    else:
        num = 1
    return f"{prefix}{num:06d}"
