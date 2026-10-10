CREATE TABLE IF NOT EXISTS simulaciones_credito (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    fecha_simulacion TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    monto_credito_semestre NUMERIC(14, 2) NOT NULL CHECK (monto_credito_semestre > 0),
    cantidad_semestres INTEGER NOT NULL CHECK (cantidad_semestres >= 1),
    monto_total_credito NUMERIC(16, 2) NOT NULL CHECK (monto_total_credito > 0),
    tasa_interes_mensual NUMERIC(10, 8) NOT NULL CHECK (tasa_interes_mensual >= 0),
    cantidad_cuotas INTEGER NOT NULL CHECK (cantidad_cuotas >= 1),
    periodo_gracia INTEGER NOT NULL CHECK (periodo_gracia >= 0),
    cuota_mensual NUMERIC(16, 2) NOT NULL CHECK (cuota_mensual >= 0),
    total_pagado NUMERIC(16, 2) NOT NULL CHECK (total_pagado >= 0),
    total_intereses NUMERIC(16, 2) NOT NULL CHECK (total_intereses >= 0)
);
