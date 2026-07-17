/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  v2312                                 |
|   \\  /    A nd           | Website:  www.openfoam.com                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      turbulenceProperties;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

simulationType      RAS;

RAS
{
    // twophasekOmega (Wilcox 2006 based): better for the adverse pressure
    // gradient / horseshoe vortex in front of the pier than k-epsilon.
    // sedFoam does not provide kOmegaSST; this is the closest available.
    // Requires 0/omega.b (provided in 0_org). Fall back to twophasekEpsilon
    // if your sedFoam build does not include twophasekOmega.
    RASModel        twophasekOmega;
//    RASModel        twophasekEpsilon;

    turbulence      on;

    printCoeffs     on;
}


// ************************************************************************* //
