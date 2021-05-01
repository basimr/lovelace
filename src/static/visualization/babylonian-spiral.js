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

function babylonianSpiral(n_steps) {
    let vecs = [ [0,0], [0,1] ];

    let n2 = 1;

    for (let step = 0; step < n_steps; step++) {
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
