-- Reference SQL for the smartphones table (built by db/build_db.py).

-- Brand-wise revenue (descending)
SELECT brand, SUM(revenue) AS revenue, SUM(units_sold) AS units
FROM smartphones
GROUP BY brand
ORDER BY revenue DESC;

-- Revenue by price segment
SELECT segment, SUM(revenue) AS revenue, SUM(units_sold) AS units
FROM smartphones
GROUP BY segment
ORDER BY revenue DESC;

-- Market share by revenue (top 8 brands)
WITH brand_rev AS (
    SELECT brand, SUM(revenue) AS revenue
    FROM smartphones
    GROUP BY brand
)
SELECT brand,
       revenue,
       ROUND(100.0 * revenue / SUM(revenue) OVER (), 1) AS share_pct
FROM brand_rev
ORDER BY revenue DESC
LIMIT 8;

-- Quarterly units sold by segment (units in thousands in source columns)
SELECT segment,
       SUM(q1) * 1000 AS q1_units,
       SUM(q2) * 1000 AS q2_units,
       SUM(q3) * 1000 AS q3_units,
       SUM(q4) * 1000 AS q4_units
FROM smartphones
GROUP BY segment
ORDER BY segment;

-- Top 3 products per segment by revenue
SELECT segment, model, brand, revenue
FROM (
    SELECT segment, model, brand, revenue,
           ROW_NUMBER() OVER (PARTITION BY segment ORDER BY revenue DESC) AS rnk
    FROM smartphones
)
WHERE rnk <= 3
ORDER BY segment, revenue DESC;
