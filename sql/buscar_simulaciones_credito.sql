SELECT id, fecha_simulacion, monto_credito_semestre, cantidad_semestres,
       monto_total_credito, tasa_interes_mensual, cantidad_cuotas, periodo_gracia,
       cuota_mensual, total_pagado, total_intereses
FROM simulaciones_credito
ORDER BY fecha_simulacion DESC, id DESC;
