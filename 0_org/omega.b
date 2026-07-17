/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  v2506                                 |
|   \\  /    A nd           | Website:  www.openfoam.com                      |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    location    "0";
    object      omega.b;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 0 -1 0 0 0 0];

// Bulk equilibrium estimate at mid depth:
// omega = ustar/(sqrt(Cmu)*kappa*z) = 0.01617/(0.3*0.41*0.025) ~ 5.3 1/s
internalField   uniform 5.3;

boundaryField
{
    inletWater
    {
        // Equilibrium log-layer profile consistent with the U.b log-law
        // inlet: omega(z) = ustar/(sqrt(Cmu)*kappa*z), z measured from the
        // initial bed surface (z = 0), floored at ks/30 like the U inlet.
        type            codedFixedValue;
        value           uniform 5.3;
        name            logLawOmegaInlet;

        code
        #{
            const scalar ustar   = 0.01617;
            const scalar kappa   = 0.41;
            const scalar sqrtCmu = 0.3;      // sqrt(0.09)
            const scalar ks      = 1.5e-3;   // 2.5*d50, same as U.b inlet

            scalarField& w = *this;
            const vectorField& Cf = patch().Cf();
            forAll(w, i)
            {
                scalar z = max(Cf[i].z(), ks/30.0);
                w[i] = ustar/(sqrtCmu*kappa*z);
            }
        #};
    }

    inletSediment
    {
        type            fixedValue;
        value           $internalField;
    }

    outletWater
    {
        type            inletOutlet;
        inletValue      $internalField;
        value           $internalField;
    }

    outletSediment
    {
        type            inletOutlet;
        inletValue      $internalField;
        value           $internalField;
    }

    top
    {
        type            inletOutlet;
        inletValue      $internalField;
        value           $internalField;
    }

    "(sideWalls|bottom|pier)"
    {
        type            omegaWallFunction;
        value           $internalField;
    }
}

// ************************************************************************* //
