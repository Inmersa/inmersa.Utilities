select E.id_efecto as "IDEfecto",F.referencia as "Fra",F.fecha as "F-Fra",E.fecha_vencimiento as "F-Vto",E.monto as "Impte",IF(E.pago_cobro,"A Cobrar","A Pagar") as "Tipo",E.medio_pago,IF(E.pagado,"Si","No") as "Pagado",E.monto_pagado as "Tot Pagado",EA.id_asiento as "Supuesto Asiento",EA.operacion as "Supuesta Operacion",EA.importe as "Supuesto Importe" FROM Efectos E JOIN Facturas F ON (E.id_factura=F.id_factura) LEFT JOIN Efectos_asientos EA ON (E.id_efecto=EA.id_efecto) LEFT JOIN biomundo_contabilidad.Asiento A ON (EA.id_asiento=A.id_asiento) WHERE A.id_asiento IS NULL AND F.id_serie NOT IN (7,8,12) ORDER BY EA.id_asiento desc, F.fecha desc;