/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  2212                                  |
|   \\  /    A nd           | Website:  www.openfoam.com                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    arch        "LSB;label=64;scalar=64";
    class       volVectorField;
    location    "0";
    object      U.b;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 1 -1 0 0 0 0];

internalField   uniform (0 0 0);

boundaryField
{
    /*inletWater
    {
        //type            fixedValue;
        //value           uniform (0.1 0 0);
        type            uniformFixedValue;
        uniformValue    table
        (
             (0.0     (0      0 0))
             (0.5     (0.05 0 0))
             (3.0     (0.10  0 0))
             (5.0     (0.15  0 0))
             (10.0    (0.233 0 0))
        );
    }*/
    
    inletWater
    {
        //type            fixedValue;
        //value           uniform (0.4 0 0);
        type            codedFixedValue;
        value           uniform (0 0 0);
        name            logLawInlet;
        code
        #{
            const scalar ustar = 0.01617; //0.016
            const scalar kappa = 0.41;
            const scalar ks    = 1.5e-3;   // 2.5*d50
            const scalar tRamp = 2.0;
            const scalar t  = this->db().time().value();
            const scalar fr = min(t/tRamp, 1.0);
            vectorField& U = *this;
            const vectorField& Cf = patch().Cf();
            forAll(U, i)
            {
                scalar z = max(Cf[i].z(), ks/30.0);   // z=0이 초기 하상면
                U[i] = vector(fr*(ustar/kappa)*log(30.0*z/ks), 0, 0);
            }
        #};

    }

    inletSediment
    {
        type            fixedValue;
        value           uniform (0 0 0);
    }
    outletWater
    {
        type            zeroGradient;
    }
    outletSediment
    {
        type            zeroGradient;
    }
    "(sideWalls|bottom|pier)"
    {
        type            noSlip;
    }
    top
    {
        type            slip;
        //type            pressureInletOutletVelocity;
        //value           uniform (0 0 0);
    }
}


// ************************************************************************* //
