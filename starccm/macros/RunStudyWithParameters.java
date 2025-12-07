package macro;

import star.mdx.MdxMacro;
import star.mdx.MdxProject;
import star.mdx.MdxDesignStudy;
import star.mdx.MdxStudyParameterManager;
import star.mdx.MdxStudyParameter;
import star.mdx.MdxStudyParameterBase;
import star.mdx.MdxContinuousParameterValue;
import star.mdx.MdxSuccessfulDesignSet;
import star.mdx.MdxDesignSetManager;
import star.mdx.MdxDesignSet;

import star.common.Units;
import star.common.UnitsManager;
import star.common.ScalarPhysicalQuantity;

public class RunStudyWithParameters extends MdxMacro {
  private final String MIN_PREFIX = "min:";
  private final String MAX_PREFIX = "max:";
  private final String INCREMENT_PREFIX = "inc:";
  private final String UNITS_PREFIX = "units:";
  
  MdxStudyParameterManager parameterManager;
  UnitsManager unitsManager;

  public void execute() {
    MdxDesignStudy designStudy = getDesignStudy();

    // clear prior design study state
    designStudy.clearDesignStudy();

    // set passed parameter ranges
    parameterManager = designStudy.getStudyParameters();
    setParameterRanges();

    // run design study
    designStudy.runDesignStudy();

    // save study outputs to CSV
    // TODO: have design set be configurable?
    MdxDesignSetManager designSetManager = designStudy.getDesignSets();
    MdxDesignSet designSet = designSetManager.getDesignSet("Successful");
    saveStudyData(designSet);
  }

  private MdxDesignStudy getDesignStudy() {
    MdxProject project = getActiveMdxProject();
    unitsManager = project.getUnitsManager();

    // obtain design study name from JVM property, since we can't pass parameters otherwise
    String studyName = System.getProperty("studyName");

    return project.getDesignStudyManager().getDesignStudy(studyName);
  }

  private void setParameterRanges() {
    String[] passedParameters = System.getProperty("studyParameters").split(",");

    for (String parameterName : passedParameters) {
      setParameterRange(parameterName);
    }
  }

  private void setParameterRange(String parameterName) {
    // parse continuous parameter properties
    double minValue = getDoubleProperty(MIN_PREFIX + parameterName);
    double maxValue = getDoubleProperty(MAX_PREFIX + parameterName);
    double incrementValue = getDoubleProperty(INCREMENT_PREFIX + parameterName);

    // including units
    String unitName = System.getProperty(UNITS_PREFIX + parameterName);
    Units units = unitsManager.getUnits(unitName);

    // get parameter value reference from project
    MdxContinuousParameterValue parameterValue = getContinuousParameterValue(parameterName);

    // set parsed properties
    ScalarPhysicalQuantity minimum = parameterValue.getMinimumQuantity();
    minimum.setValueAndUnits(minValue, units);

    ScalarPhysicalQuantity maximum = parameterValue.getMaximumQuantity();
    maximum.setValueAndUnits(maxValue, units);

    ScalarPhysicalQuantity increment = parameterValue.getIncrementQuantity();
    increment.setValueAndUnits(incrementValue, units);
  }

  private void saveStudyData(MdxDesignSet designSet) {
    String outFileName = System.getProperty("outFile", "drag_data.csv");
    String outPath = resolvePath(outFileName);

    designSet.exportCsvFile(outPath);
  }

  private MdxContinuousParameterValue getContinuousParameterValue(String parameterName) {
    // TODO: handle failed cast gracefully
    MdxStudyParameter parameter = (MdxStudyParameter) parameterManager.getStudyParameterBase(parameterName);
    return parameter.getContinuousParameterValue();
  }

  private double getDoubleProperty(String propertyName) {
    // TODO: handle invalid double case
    String rawValue = System.getProperty(propertyName);

    return Double.parseDouble(rawValue);
  }
}
