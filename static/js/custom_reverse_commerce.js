document.addEventListener("DOMContentLoaded", function () {
    const table = new Tabulator("#reverse-orders-table", {
        ajaxURL: "/api/reverse-orders",
        layout: "fitColumns",
        pagination: "local",
        paginationSize: 20,
        columns: [
            { title: "Order ID", field: "order_id", sorter: "number" },
            {
                title: "Date",
                field: "datetime",
                sorter: "date",
                formatter: "datetime",
                formatterParams: {
                    inputFormat: "iso",
                    outputFormat: "yyyy-MM-dd HH:mm",
                },
            },
            { title: "Status", field: "status_name", sorter: "string" },
            { title: "Customer", field: "customer_name", sorter: "string" },
            { title: "Model", field: "model_name", sorter: "string" },
            { title: "Storage", field: "storage", sorter: "number" },
            { title: "Color", field: "color_name", sorter: "string" },
            { title: "Base Price", field: "base_price", sorter: "number", formatter: "money", formatterParams: { symbol: "€" } },
            { title: "Price", field: "price", sorter: "number", formatter: "money", formatterParams: { symbol: "€" } },
            {
                title: "Image",
                field: "order_id",
                formatter: function (cell) {
                    let orderId = cell.getValue();
                    let imageUrl = `/api/get-image/${orderId}`;
                    return `<button onclick="showImageSwal('${imageUrl}')">Visualizza</button>`;
                },
            },
        ],
    });
});

function showImageSwal(imageUrl) {
    Swal.fire({
        // title: "Order Image",
        imageUrl: imageUrl,
        imageAlt: "Order Image",
        showCloseButton: true,
        showConfirmButton: false,
    });
}

function renderTable(data) {
    const container = document.getElementById("customerDefectsTable");
    if (hot) hot.destroy();

    hot = new Handsontable(container, {
        data: data,
        colHeaders: [
            'Order Id', 'Price', 'Status', 'Customer', 'Serie', 'Supplier', 'Proforma', 'Insertion Date',
            'Detection Date', 'Description', 'Swap', 'New Battery Test', 'Topics', 'N. difetti', '%'
        ],
        columns: [
            { data: 'store', readOnly: true },
            { data: 'order_number', readOnly: true },
            { data: 'imei', readOnly: true },
            { data: 'sku', readOnly: true },
            { data: 'model', readOnly: true },
            { data: 'supplier', readOnly: true },
            { data: 'proforma', readOnly: true },
            { data: 'insertion_date' },
            { data: 'detection_date' },
            { data: 'description' },
            { data: 'swap' },
            { data: 'new_battery_test' },
            { data: 'topics' },
            { data: 'count', readOnly: true },
            { data: 'percentage', readOnly: true }
        ],
        columnSorting: true,
        hiddenColumns: { columns: getHiddenColumns(), indicators: true },
        colWidths: [90, 100, 130, 150, 60, 130, 100, 100, 190, 90, 115, 70],
        stretchH: "all",
        width: "100%",
        rowHeights: 23,
        licenseKey: "non-commercial-and-evaluation",
        afterChange: function (changes, source) {
            if (source === 'loadData') {
                return;
            }

            changes.forEach(([row, prop, oldValue, newValue]) => {
                if (newValue !== oldValue) {
                    console.log(data[row]);
                    fetch(`/api/customer_defects/${data[row].id}`, {
                        method: 'PATCH',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ [prop]: newValue }),
                    })
                        .then(response => {
                            if (!response.ok) {
                                throw new Error('Errore durante l\'aggiornamento dei dati');
                            }
                        })
                        .catch(error => {
                            console.error('Errore durante l\'aggiornamento dei dati:', error);
                        });
                }
            });
        }
    });
}