function logisticGrowthAnalytic(P0, r, K, t) {
    return K / (1 + ((K - P0) / P0) * Math.exp(-r*t))
}

function logisticGrowthForwardEuler(P0, r, K, dt, N) {
    var P = new Array(N)

    P[0] = P0;
    for (n = 0; n < N; n++) {
        P[n+1] = P[n] + dt * r * P[n] * (1 - P[n] / K)
    }

    return P
}

function plotLogisticGrowth(P0, r, K, dt, N) {
    var times = new Array(N)
    for (n = 0; n <= N; n++) {
        times[n] = n * dt
    }

    var traceAnalytic = {
        x: times,
        y: times.map(t => logisticGrowthAnalytic(P0, r, K, t)),
        type: 'lines',
        name: 'analytic'
    }

    var traceNumerical = {
        x: times,
        y: logisticGrowthForwardEuler(P0, r, K, dt, N),
        type: 'lines',
        name: 'numerical'
    }

    var layout = {
        title: 'Logistic growth',
        xaxis: { title: 'Time t' },
        yaxis: { title: 'P(t)' },
        paper_bgcolor: 'rgba(0, 0, 0, 0)',
        plot_bgcolor: 'rgba(0, 0, 0, 0)'
    }

    Plotly.newPlot("logistic-growth-app", [traceAnalytic, traceNumerical], layout)

    return
}

plotLogisticGrowth(10, 2, 100, 0.1, 50)

var sliderInitialPopulation = document.getElementById("slider-initial-population");
var sliderGrowthRate = document.getElementById("slider-growth-rate");
var sliderCarryingCapacity = document.getElementById("slider-carrying-capacity");
var sliderTimeStep = document.getElementById("slider-time-step");
var sliderIterations = document.getElementById("slider-iterations");

noUiSlider.create(sliderInitialPopulation, {
    start: [10],
    range: {
        "min": [0],
        "max": [100]
    },
    step: 0.1
});

noUiSlider.create(sliderGrowthRate, {
    start: [2],
    range: {
        "min": [-5],
        "max": [5]
    },
    step: 0.01
});

noUiSlider.create(sliderCarryingCapacity, {
    start: [100],
    range: {
        "min": [0],
        "max": [1000]
    },
    step: 1
});

noUiSlider.create(sliderTimeStep, {
    start: [0.1],
    range: {
        "min": [0.01],
        "max": [1]
    },
    step: 0.01
});

noUiSlider.create(sliderIterations, {
    start: [50],
    range: {
        "min": [1],
        "max": [100]
    },
    step: 1
});

var labelInitialPopulation = document.getElementById("label-initial-population");
var labelGrowthRate = document.getElementById("label-growth-rate");
var labelCarryingCapacity = document.getElementById("label-carrying-capacity");
var labelTimeStep = document.getElementById("label-time-step");
var labelIterations = document.getElementById("label-iterations");

function replotLogisticGrowth() {
    var P0 = parseFloat(sliderInitialPopulation.noUiSlider.get());
    var r = parseFloat(sliderGrowthRate.noUiSlider.get());
    var K = parseFloat(sliderCarryingCapacity.noUiSlider.get());
    var dt = parseFloat(sliderTimeStep.noUiSlider.get());
    var N = parseFloat(sliderIterations.noUiSlider.get());

    labelInitialPopulation.innerHTML = P0;
    labelGrowthRate.innerHTML = r;
    labelCarryingCapacity.innerHTML = K;
    labelTimeStep.innerHTML = dt;
    labelIterations.innerHTML = N;

    plotLogisticGrowth(P0, r, K, dt, N);

    return
}

sliderInitialPopulation.noUiSlider.on("update", replotLogisticGrowth);
sliderGrowthRate.noUiSlider.on("update", replotLogisticGrowth);
sliderCarryingCapacity.noUiSlider.on("update", replotLogisticGrowth);
sliderTimeStep.noUiSlider.on("update", replotLogisticGrowth);
sliderIterations.noUiSlider.on("update", replotLogisticGrowth);
