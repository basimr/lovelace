/////
///// Babylonian spiral
/////

// In Javascript, % is actually a remainder operator.
// See: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Remainder
function modulo(a, n) {
    return ((a % n ) + n ) % n;
}

function pythagoreanTriples(c2) {
    let triples = [];

    let c = Math.trunc(Math.sqrt(c2));
    let a = 0;
    let b = c+1;

    while (true) {
        if (a**2 > Math.floor(c2 / 2)) {
            break;
        }

        while (true) {
            if (a**2 + b**2 < c2) {
                break;
            } else if (a**2 + b**2 == c2) {
                if (a == 0) {
                    triples.push([b, 0], [-b, 0], [0, b], [0, -b]);
                } else if (b == 0) {
                    triples.push([a, 0], [-a, 0], [0, a], [0, -a]);
                } else if (a == b) {
                    triples.push([a, a], [a, -a], [-a, a], [-a, -a]);
                } else {
                    triples.push([a, b], [a, -b], [-a, b], [-a, -b],
                                 [b, a], [b, -a], [-b, a], [-b, -a]);
                }
            }
            b -= 1;
        }
        a += 1;
    }
    
    return triples;
}

function babylonianSpiral(nSteps) {
    let vecs = [ [0,0], [0,1] ];

    let n2 = 1;

    for (let step = 0; step < nSteps; step++) {
        let x0 = vecs[vecs.length-1][0];
        let y0 = vecs[vecs.length-1][1];
        let theta = Math.atan2(y0, x0);

        let pairs = [];
        while (pairs.length == 0) {
            n2 += 1;
            pairs = pythagoreanTriples(n2);
        }

        let nextVec = [];
        let minDeltaTheta = Infinity;
        for (let i = 0; i < pairs.length; i++) {
            let vec = pairs[i];
            let deltaTheta = modulo(theta - Math.atan2(vec[1], vec[0]), 2*Math.PI);
            if (deltaTheta < minDeltaTheta) {
                minDeltaTheta = deltaTheta;
                nextVec = vec;
            }
        }

        vecs.push(nextVec);
    }

    let x = [vecs[0][0]];
    let y = [vecs[0][1]];

    for (let i = 1; i < vecs.length; i++) {
        x.push(x[i-1] + vecs[i][0]);
        y.push(y[i-1] + vecs[i][1]);
    }

    return [x, y];
}

/////
///// Interactive figure
/////

let maxSteps = 10_000;

let t0 = performance.now();
let xy = babylonianSpiral(maxSteps);
let t1 = performance.now();

console.log(`Computing ${maxSteps} steps of the Babylonian spiral took ${t1 - t0} ms.`);

let xSpiral = xy[0];
let ySpiral = xy[1];

function plotBabylonianSpiral(nSteps) {

    let trace = {
        x: xSpiral.slice(0, 2 + nSteps),
        y: ySpiral.slice(0, 2 + nSteps),
        mode: 'lines',
        type: 'scatter'
    }

    let layout = {
        xaxis: { title: 'x' },
        yaxis: { title: 'y' },
        paper_bgcolor: 'rgba(0, 0, 0, 0)',
        plot_bgcolor: 'rgba(0, 0, 0, 0)',
        yaxis: {
            scaleanchor: "x",
            scaleratio: 1
        }
    }

    Plotly.newPlot("babylonian-spiral-app", [trace], layout)

    return
}

plotBabylonianSpiral(20)

let sliderSteps = document.getElementById("slider-steps");

noUiSlider.create(sliderSteps, {
    start: [20],
    range: {
        "min": [0],
        "max": [maxSteps]
    },
    step: 1
});

let labelSteps = document.getElementById("label-steps");

function replotBabylonianSpiral() {
    let nSteps = parseFloat(sliderSteps.noUiSlider.get());

    labelSteps.innerHTML = nSteps;

    plotBabylonianSpiral(nSteps)

    return
}

sliderSteps.noUiSlider.on("update", replotBabylonianSpiral);

/////
///// Test case visualization
/////

function visualize_test_case(input, output, expected, nTestCase) {

    let nSteps = input[0];
    let xOutput = output[0];
    let yOutput = output[1];

    document.getElementById(`input${nTestCase}`).innerHTML =
        `<b>Input</b>: n_steps = ${nSteps} <br>`

    document.getElementById(`output${nTestCase}`).innerHTML =
        `<b>Output</b>: <br>` +
        `<div id="output-plot-${nTestCase}"></div>`

    let traceCorrect = {
        x: xSpiral.slice(0, 2 + nSteps),
        y: ySpiral.slice(0, 2 + nSteps),
        mode: 'lines',
        type: 'scatter',
        name: 'correct'
    }

    let traceOutput = {
        x: xOutput,
        y: yOutput,
        mode: 'lines',
        type: 'scatter',
        name: 'output'
    }

    let layout = {
        xaxis: { title: 'x' },
        yaxis: { title: 'y' },
        paper_bgcolor: 'rgba(0, 0, 0, 0)',
        plot_bgcolor: 'rgba(0, 0, 0, 0)',
        yaxis: {
            scaleanchor: "x",
            scaleratio: 1
        }
    }

    Plotly.newPlot(`output-plot-${nTestCase}`, [traceCorrect, traceOutput], layout)

    return
}
