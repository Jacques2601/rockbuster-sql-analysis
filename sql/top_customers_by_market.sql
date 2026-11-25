-- Portfolio revision: rank countries and cities by customer count,
-- then rank paying customers within those cities by total payment.
-- Uses geographic IDs and deterministic tie-breaks.
-- Static review only; execution against DVD Rental remains outstanding.
WITH top_countries AS (
    SELECT co.country_id
    FROM customer cu
    JOIN address a ON a.address_id = cu.address_id
    JOIN city ci ON ci.city_id = a.city_id
    JOIN country co ON co.country_id = ci.country_id
    GROUP BY co.country_id
    ORDER BY COUNT(*) DESC, co.country_id
    LIMIT 10
), top_cities AS (
    SELECT ci.city_id
    FROM customer cu
    JOIN address a ON a.address_id = cu.address_id
    JOIN city ci ON ci.city_id = a.city_id
    JOIN top_countries tc ON tc.country_id = ci.country_id
    GROUP BY ci.city_id
    ORDER BY COUNT(*) DESC, ci.city_id
    LIMIT 10
), customer_payments AS (
    SELECT cu.customer_id, cu.first_name, cu.last_name,
           ci.city, co.country, SUM(p.amount) AS total_payment
    FROM customer cu
    JOIN address a ON a.address_id = cu.address_id
    JOIN city ci ON ci.city_id = a.city_id
    JOIN country co ON co.country_id = ci.country_id
    JOIN top_cities tc ON tc.city_id = ci.city_id
    JOIN payment p ON p.customer_id = cu.customer_id
    GROUP BY cu.customer_id, cu.first_name, cu.last_name, ci.city, co.country
), top_customers AS (
    SELECT * FROM customer_payments
    ORDER BY total_payment DESC, customer_id
    LIMIT 5
)
SELECT *, AVG(total_payment) OVER () AS average_top_customer_payment
FROM top_customers
ORDER BY total_payment DESC, customer_id;
